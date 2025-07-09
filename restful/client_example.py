"""
API客户端示例代码
演示如何使用法律咨询API
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class LegalConsultationClient:
    """法律咨询API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._make_request("GET", "/health")
    
    def query_law(self, question: str, session_id: Optional[str] = None, 
                  show_results: bool = True) -> Dict[str, Any]:
        """法律咨询查询"""
        data = {
            "question": question,
            "show_results": show_results
        }
        if session_id:
            data["session_id"] = session_id
        
        response = self._make_request("POST", "/query", json=data)
        
        # 保存会话ID
        if not self.session_id:
            self.session_id = response.get("session_id")
        
        return response
    
    def search_laws(self, query: str, k: int = 5) -> Dict[str, Any]:
        """搜索法律文档"""
        data = {
            "query": query,
            "k": k
        }
        return self._make_request("POST", "/search", json=data)
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取会话总结"""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        return self._make_request("GET", f"/sessions/{sid}/summary")
    
    def delete_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """删除会话"""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        response = self._make_request("DELETE", f"/sessions/{sid}")
        
        # 清除本地会话ID
        if sid == self.session_id:
            self.session_id = None
        
        return response
    
    def list_sessions(self) -> Dict[str, Any]:
        """列出所有活跃会话"""
        return self._make_request("GET", "/sessions")
    
    def reset_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """重置会话"""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        return self._make_request("POST", f"/sessions/{sid}/reset")

def main():
    """示例使用方法"""
    # 创建客户端
    client = LegalConsultationClient()
    
    try:
        # 健康检查
        print("=== 健康检查 ===")
        health = client.health_check()
        print(f"服务状态: {health['status']}")
        print(f"API版本: {health['version']}")
        print()
        
        # 法律咨询查询
        print("=== 法律咨询查询 ===")
        question = "如果我在工作中受伤了，有哪些法律权利和保障？"
        response = client.query_law(question)
        print(f"问题: {question}")
        print(f"会话ID: {response['session_id']}")
        print(f"回答: {response['answer'][:200]}...")
        print()
        
        # 搜索法律文档
        print("=== 搜索法律文档 ===")
        search_query = "工伤保障"
        search_results = client.search_laws(search_query, k=3)
        print(f"搜索查询: {search_query}")
        print(f"找到 {search_results['total']} 条相关法条")
        for i, result in enumerate(search_results['results'], 1):
            print(f"{i}. {result['filename']} (相关度: {result['score']:.4f})")
            print(f"   内容: {result['content'][:100]}...")
        print()
        
        # 继续对话
        print("=== 继续对话 ===")
        follow_up = "具体的工伤认定流程是什么？"
        response2 = client.query_law(follow_up, session_id=client.session_id)
        print(f"问题: {follow_up}")
        print(f"回答: {response2['answer'][:200]}...")
        print()
        
        # 获取会话总结
        print("=== 会话总结 ===")
        summary = client.get_session_summary()
        print(f"总结: {summary['summary']}")
        print()
        
        # 列出所有会话
        print("=== 所有会话 ===")
        sessions = client.list_sessions()
        print(f"活跃会话数: {sessions['total']}")
        for session in sessions['sessions']:
            print(f"会话ID: {session['session_id']}")
            print(f"消息数: {session['message_count']}")
            print(f"最后活动: {session['last_activity']}")
        print()
        
        # 清理会话
        print("=== 清理会话 ===")
        delete_response = client.delete_session()
        print(f"删除结果: {delete_response['message']}")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        print("请确保API服务正在运行 (python main.py)")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
