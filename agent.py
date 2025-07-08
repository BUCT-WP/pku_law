import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

# 设置环境变量来避免 tokenizers 警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 导入langchain相关组件
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage

@dataclass
class ConversationContext:
    """对话上下文管理"""
    history: List[Dict[str, str]] = field(default_factory=list)
    current_topic: str = ""
    retrieved_context: List[str] = field(default_factory=list)
    last_query: str = ""
    session_id: str = ""
    
    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_recent_context(self, n: int = 3) -> str:
        """获取最近n轮对话的上下文"""
        recent = self.history[-n*2:] if len(self.history) >= n*2 else self.history
        context_str = ""
        for msg in recent:
            context_str += f"{msg['role']}: {msg['content']}\n"
        return context_str

class FAISSRetriever:
    """FAISS检索器"""
    
    def __init__(self, index_path: str = 'law_index.bin', metadata_path: str = 'metadata.pkl'):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.index = faiss.read_index(index_path)
        
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关法条"""
        query_vec = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vec), k)
        
        results = []
        for idx, i in enumerate(indices[0]):
            if i < len(self.metadata):
                results.append({
                    'content': self.metadata[i]['content'],
                    'filename': self.metadata[i]['filename'],
                    'score': 1 / (1 + distances[0][idx]),
                    'distance': distances[0][idx]
                })
        
        return results

class RetrievalAgent:
    """检索Agent"""
    
    def __init__(self, retriever: FAISSRetriever):
        self.retriever = retriever
    
    def retrieve_relevant_laws(self, query: str, context: ConversationContext) -> str:
        """检索相关法条"""
        # 结合上下文优化检索查询
        enhanced_query = query
        if context.current_topic:
            enhanced_query = f"{context.current_topic} {query}"
        
        results = self.retriever.search(enhanced_query, k=3)
        
        # 格式化检索结果
        formatted_results = []
        for result in results:
            formatted_results.append(f"法条内容: {result['content'][:500]}...")
        
        # 更新上下文
        context.retrieved_context = [r['content'] for r in results]
        context.last_query = query
        
        return "\n\n".join(formatted_results)
    
    def display_search_results(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """展示检索结果的详细信息"""
        results = self.retriever.search(query, k=k)
        
        print(f"\n📋 检索结果 (共找到 {len(results)} 条相关法条):")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n【法条 {i}】")
            print(f"📖 来源文件: {result['filename']}")
            print(f"🎯 相关度评分: {result['score']:.4f}")
            print(f"📄 内容:")
            print("-" * 40)
            print(result['content'])
            print("-" * 40)
        
        return results

class QAAgent:
    """问答Agent"""
    
    def __init__(self, llm):
        self.llm = llm
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "history", "question"],
            template="""你是一个专业的法律咨询助手。基于以下信息回答问题：

对话历史：
{history}

相关法条：
{context}

问题：{question}

请根据相关法条，结合对话历史，给出准确、专业的法律建议。如果法条不足以完全回答问题，请明确说明。

回答："""
        )
        self.qa_chain = LLMChain(llm=self.llm, prompt=self.qa_prompt)
    
    def answer_question(self, question: str, context: ConversationContext, retrieved_context: str) -> str:
        """回答法律问题"""
        history = context.get_recent_context(3)
        print(retrieved_context)
        response = self.qa_chain.invoke({
            "context": retrieved_context,
            "history": history,
            "question": question
        })
        
        return response["text"]

class SummaryAgent:
    """总结Agent"""
    
    def __init__(self, llm):
        self.llm = llm
        self.summary_prompt = PromptTemplate(
            input_variables=["conversation", "key_points"],
            template="""请总结以下法律咨询对话的要点：

对话内容：
{conversation}

重要法条：
{key_points}

请提供简洁的总结，包括：
1. 咨询的主要法律问题
2. 涉及的相关法条
3. 给出的建议要点

总结："""
        )
        self.summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
    
    def summarize_conversation(self, context: ConversationContext) -> str:
        """总结对话内容"""
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in context.history
        ])
        
        key_points = "\n".join(context.retrieved_context[:3])
        
        summary = self.summary_chain.invoke({
            "conversation": conversation,
            "key_points": key_points
        })
        
        return summary["text"]

class LegalConsultationSystem:
    """法律咨询系统主类"""
    
    def __init__(self, openai_api_key: str):
        # 初始化LLM
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            base_url="https://api.siliconflow.cn/v1",
            model_name="Tongyi-Zhiwen/QwenLong-L1-32B",
            temperature=0.1,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # 初始化各个Agent
        self.retriever = FAISSRetriever()
        self.retrieval_agent = RetrievalAgent(self.retriever)
        self.qa_agent = QAAgent(self.llm)
        self.summary_agent = SummaryAgent(self.llm)
        
        # 上下文管理
        self.context = ConversationContext()
        
        # 记忆管理
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )
    
    def process_query(self, query: str) -> str:
        """处理用户查询"""
        try:
            # 1. 检索相关法条
            print("🔍 正在检索相关法条...")
            retrieved_context = self.retrieval_agent.retrieve_relevant_laws(query, self.context)
            
            # 2. 生成回答
            print("🤖 正在生成法律建议...")
            answer = self.qa_agent.answer_question(query, self.context, retrieved_context)
            
            # 3. 更新上下文
            self.context.add_message("user", query)
            self.context.add_message("assistant", answer)
            
            # 4. 更新记忆
            self.memory.save_context({"input": query}, {"output": answer})
            
            return answer
            
        except Exception as e:
            error_msg = f"处理查询时发生错误: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def search_and_display(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索并展示法律文档检索结果"""
        return self.retrieval_agent.display_search_results(query, k)
    
    def process_query_with_display(self, query: str, show_results: bool = True) -> str:
        """处理查询并可选择展示检索结果"""
        try:
            # 1. 检索并展示相关法条
            print("🔍 正在检索相关法条...")
            if show_results:
                self.search_and_display(query, k=3)
            
            retrieved_context = self.retrieval_agent.retrieve_relevant_laws(query, self.context)
            
            # 2. 生成回答
            print("🤖 正在生成法律建议...")
            answer = self.qa_agent.answer_question(query, self.context, retrieved_context)
            
            # 3. 更新上下文
            self.context.add_message("user", query)
            self.context.add_message("assistant", answer)
            
            # 4. 更新记忆
            self.memory.save_context({"input": query}, {"output": answer})
            
            return answer
            
        except Exception as e:
            error_msg = f"处理查询时发生错误: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def get_conversation_summary(self) -> str:
        """获取对话总结"""
        if not self.context.history:
            return "暂无对话记录"
        
        return self.summary_agent.summarize_conversation(self.context)
    
    def reset_context(self):
        """重置对话上下文"""
        self.context = ConversationContext()
        self.memory.clear()
    
    def save_session(self, filepath: str):
        """保存会话"""
        session_data = {
            "context": self.context.__dict__,
            "timestamp": datetime.now().isoformat()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def load_session(self, filepath: str):
        """加载会话"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 恢复上下文
            context_dict = session_data["context"]
            self.context = ConversationContext(**context_dict)
            
            # 恢复记忆
            for msg in self.context.history:
                if msg["role"] == "user":
                    user_msg = msg["content"]
                elif msg["role"] == "assistant":
                    assistant_msg = msg["content"]
                    self.memory.save_context({"input": user_msg}, {"output": assistant_msg})
                    
        except Exception as e:
            print(f"加载会话失败: {str(e)}")

