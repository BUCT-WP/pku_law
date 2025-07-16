import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="法律咨询助手",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f4e79, #4a90e2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .search-result {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #4caf50;
    }
    
    .status-inactive {
        background-color: #f44336;
    }
    
    .session-item {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.2rem 0;
        transition: all 0.3s ease;
    }
    
    .session-item:hover {
        background-color: #e9ecef;
        border-color: #6c757d;
    }
    
    .session-item.current {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
    }
    
    .session-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.2rem;
    }
    
    .session-detail {
        font-size: 0.8em;
        color: #666;
        margin: 0.1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class LegalConsultationClient:
    """法律咨询API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def check_health(self) -> Dict:
        """检查API健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "data": response.json() if response.status_code == 200 else None,
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e)
            }
    
    def query_law(self, question: str, session_id: Optional[str] = None, show_results: bool = True) -> Dict:
        """发送法律咨询查询"""
        try:
            payload = {
                "question": question,
                "show_results": show_results
            }
            if session_id:
                payload["session_id"] = session_id
                
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=60  # 增加超时时间到60秒
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def search_laws(self, query: str, k: int = 5) -> Dict:
        """搜索法律文档"""
        try:
            payload = {
                "query": query,
                "k": k
            }
            
            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话总结"""
        try:
            response = requests.get(
                f"{self.base_url}/sessions/{session_id}/summary",
                timeout=20
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def list_sessions(self) -> Dict:
        """列出所有会话"""
        try:
            response = requests.get(f"{self.base_url}/sessions", timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def reset_session(self, session_id: str) -> Dict:
        """重置会话"""
        try:
            response = requests.post(
                f"{self.base_url}/sessions/{session_id}/reset",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def get_session_history(self, session_id: str) -> Dict:
        """获取会话历史消息"""
        try:
            response = requests.get(
                f"{self.base_url}/sessions/{session_id}/history",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": response.json().get("detail", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

def init_session_state():
    """初始化会话状态"""
    if 'client' not in st.session_state:
        st.session_state.client = LegalConsultationClient()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'api_status' not in st.session_state:
        st.session_state.api_status = "checking"

def display_api_status():
    """显示API状态"""
    health = st.session_state.client.check_health()
    
    if health["status"] == "healthy":
        st.session_state.api_status = "healthy"
        status_class = "status-active"
        status_text = "服务正常"
    else:
        st.session_state.api_status = "error"
        status_class = "status-inactive"
        status_text = f"服务异常: {health.get('error', '未知错误')}"
    
    st.sidebar.markdown(f"""
    <div class="sidebar-section">
        <h3>🌐 API状态</h3>
        <div>
            <span class="status-indicator {status_class}"></span>
            <span>{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_session_list():
    """显示会话列表"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 📋 会话列表")
    
    # 获取所有会话
    sessions_result = st.session_state.client.list_sessions()
    
    if sessions_result["success"]:
        sessions_data = sessions_result["data"]
        sessions = sessions_data.get("sessions", [])
        
        if sessions:
            st.sidebar.markdown(f"共有 **{len(sessions)}** 个会话")
            
            # 显示会话列表
            for i, session in enumerate(sessions):
                session_id = session["session_id"]
                message_count = session.get("message_count", 0)
                last_activity = session.get("last_activity", "未知")
                
                # 检查是否为当前会话
                is_current = (st.session_state.session_id == session_id)
                
                # 会话显示
                session_icon = "🟢" if is_current else "⚪"
                session_class = "session-item current" if is_current else "session-item"
                
                # 会话卡片
                session_display = f"""
                <div class="{session_class}">
                    <div class="session-title">
                        {session_icon} 会话 {i+1}
                    </div>
                    <div class="session-detail">
                        ID: {session_id[:8]}...
                    </div>
                    <div class="session-detail">
                        消息: {message_count} 条
                    </div>
                </div>
                """
                
                st.sidebar.markdown(session_display, unsafe_allow_html=True)
                
                # 如果不是当前会话，提供切换按钮
                if not is_current:
                    if st.sidebar.button(f"🔄 切换", key=f"switch_session_{session_id}", help=f"切换到会话 {i+1}"):
                        # 切换会话
                        st.session_state.session_id = session_id
                        
                        # 获取会话历史
                        history_result = st.session_state.client.get_session_history(session_id)
                        if history_result["success"]:
                            history_data = history_result["data"]
                            st.session_state.messages = history_data.get("messages", [])
                        else:
                            st.session_state.messages = []
                            st.sidebar.warning(f"无法加载会话历史: {history_result['error']}")
                        
                        st.sidebar.success(f"已切换到会话 {i+1}")
                        st.rerun()
                else:
                    st.sidebar.markdown("**📍 当前活跃**")
                
                # 添加间距
                st.sidebar.markdown("<br>", unsafe_allow_html=True)
        else:
            st.sidebar.info("📝 暂无会话记录\n\n开始一个新对话来创建第一个会话！")
    else:
        st.sidebar.error(f"❌ 获取会话列表失败\n\n{sessions_result['error']}")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def display_sidebar():
    """显示侧边栏"""
    st.sidebar.markdown('<div class="main-header">⚖️ 控制面板</div>', unsafe_allow_html=True)
    
    # API状态检查
    display_api_status()
    
    # API设置
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### ⚙️ API设置")
    
    current_url = st.session_state.client.base_url
    new_url = st.sidebar.text_input("API地址", value=current_url, key="api_url")
    
    if new_url != current_url:
        st.session_state.client = LegalConsultationClient(new_url)
        st.rerun()
    
    if st.sidebar.button("🔄 刷新状态"):
        st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # 会话管理
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 💬 会话管理")
    
    if st.sidebar.button("🆕 新建会话"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.success("已创建新会话")
    
    if st.session_state.session_id and st.sidebar.button("🔄 重置当前会话"):
        result = st.session_state.client.reset_session(st.session_state.session_id)
        if result["success"]:
            st.session_state.messages = []
            st.success("会话已重置")
        else:
            st.error(f"重置失败: {result['error']}")
    
    # 显示会话信息
    if st.session_state.session_id:
        st.sidebar.markdown(f"**当前会话ID:** `{st.session_state.session_id[:8]}...`")
        st.sidebar.markdown(f"**消息数量:** {len(st.session_state.messages)}")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # 会话列表
    if st.session_state.api_status == "healthy":
        display_session_list()
    
    # 统计信息
    if st.session_state.api_status == "healthy":
        sessions_result = st.session_state.client.list_sessions()
        if sessions_result["success"]:
            sessions_data = sessions_result["data"]
            
            st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.sidebar.markdown("### 📊 统计信息")
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.markdown(f'<div class="metric-card">活跃会话<br><strong>{sessions_data["total"]}</strong></div>', unsafe_allow_html=True)
            with col2:
                current_session_msgs = len(st.session_state.messages)
                st.markdown(f'<div class="metric-card">当前对话<br><strong>{current_session_msgs}</strong></div>', unsafe_allow_html=True)
            
            st.sidebar.markdown('</div>', unsafe_allow_html=True)

def display_chat_interface():
    """显示聊天界面"""
    st.markdown('<div class="main-header">⚖️ 法律咨询助手</div>', unsafe_allow_html=True)
    
    # 检查API状态
    if st.session_state.api_status != "healthy":
        st.error("⚠️ API服务不可用，请检查服务状态或联系管理员")
        return
    
    # 显示历史消息
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 您:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>⚖️ 法律助手:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>👋 欢迎使用法律咨询助手</h3>
            <p>请在下方输入您的法律问题，我将为您提供专业的法律建议。</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 输入区域
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "请输入您的法律问题:",
                placeholder="例如：关于劳动合同解除的相关法律规定是什么？",
                height=100,
                key="user_input"
            )
        
        with col2:
            st.write("") # 空行用于对齐
            st.write("") # 空行用于对齐
            show_results = st.checkbox("显示检索结果", value=True)
            submit_button = st.form_submit_button("🚀 发送", use_container_width=True)
    
    # 处理用户输入
    if submit_button and user_input.strip():
        # 添加用户消息到聊天历史
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # 显示加载状态
        with st.spinner("🤔 正在思考您的问题..."):
            # 调用API
            result = st.session_state.client.query_law(
                question=user_input,
                session_id=st.session_state.session_id,
                show_results=show_results
            )
        
        if result["success"]:
            response_data = result["data"]
            
            # 更新会话ID
            if not st.session_state.session_id:
                st.session_state.session_id = response_data["session_id"]
            
            # 添加助手回复到聊天历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["answer"],
                "timestamp": response_data["timestamp"]
            })
            
            st.rerun()
        else:
            st.error(f"❌ 查询失败: {result['error']}")

def display_search_interface():
    """显示搜索界面"""
    st.markdown('<div class="main-header">🔍 法律文档搜索</div>', unsafe_allow_html=True)
    
    if st.session_state.api_status != "healthy":
        st.error("⚠️ API服务不可用，请检查服务状态")
        return
    
    # 搜索表单
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "搜索关键词:",
                placeholder="例如：劳动合同、知识产权、公司法等",
                key="search_query"
            )
        
        with col2:
            search_k = st.selectbox("结果数量", options=[5, 10, 15, 20], index=0)
        
        search_button = st.form_submit_button("🔍 搜索", use_container_width=True)
    
    # 处理搜索
    if search_button and search_query.strip():
        with st.spinner("🔍 正在搜索相关法律文档..."):
            result = st.session_state.client.search_laws(search_query, k=search_k)
        
        if result["success"]:
            search_data = result["data"]
            results = search_data["results"]
            
            if results:
                st.success(f"✅ 找到 {len(results)} 条相关法律条文")
                
                # 显示搜索结果统计
                scores = [r["score"] for r in results]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("结果数量", len(results))
                with col2:
                    st.metric("平均相关度", f"{sum(scores)/len(scores):.3f}")
                with col3:
                    st.metric("最高相关度", f"{max(scores):.3f}")
                
                # 相关度分布图
                if len(results) > 1:
                    fig = px.bar(
                        x=range(1, len(results) + 1),
                        y=scores,
                        labels={"x": "结果排序", "y": "相关度分数"},
                        title="搜索结果相关度分布"
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                # 显示搜索结果
                for i, result in enumerate(results, 1):
                    with st.expander(f"📄 结果 {i} - {result['filename']} (相关度: {result['score']:.3f})"):
                        st.markdown(f"""
                        <div class="search-result">
                            <p><strong>文件名:</strong> {result['filename']}</p>
                            <p><strong>相关度:</strong> {result['score']:.3f}</p>
                            <p><strong>距离值:</strong> {result['distance']:.3f}</p>
                            <hr>
                            <p><strong>内容:</strong></p>
                            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 4px; white-space: pre-wrap;">
{result['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("❌ 未找到相关法律条文，请尝试其他关键词")
        else:
            st.error(f"❌ 搜索失败: {result['error']}")

def display_summary_interface():
    """显示会话总结界面"""
    st.markdown('<div class="main-header">📋 会话总结</div>', unsafe_allow_html=True)
    
    if st.session_state.api_status != "healthy":
        st.error("⚠️ API服务不可用，请检查服务状态")
        return
    
    if not st.session_state.session_id:
        st.warning("⚠️ 当前没有活跃的会话，请先进行一些对话")
        return
    
    if not st.session_state.messages:
        st.warning("⚠️ 当前会话没有对话内容")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**当前会话ID:** `{st.session_state.session_id}`")
        st.markdown(f"**对话轮数:** {len([m for m in st.session_state.messages if m['role'] == 'user'])}")
        st.markdown(f"**总消息数:** {len(st.session_state.messages)}")
    
    with col2:
        if st.button("📋 生成总结", use_container_width=True):
            with st.spinner("📝 正在生成会话总结..."):
                result = st.session_state.client.get_session_summary(st.session_state.session_id)
            
            if result["success"]:
                summary_data = result["data"]
                
                st.markdown("### 📋 会话总结")
                st.markdown(f"""
                <div style="background-color: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="white-space: pre-wrap; margin: 0;">{summary_data['summary']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**生成时间:** {summary_data['timestamp']}")
            else:
                st.error(f"❌ 生成总结失败: {result['error']}")
    
    # 显示对话历史统计
    if st.session_state.messages:
        st.markdown("### 📊 对话统计")
        
        # 计算统计信息
        user_msgs = [m for m in st.session_state.messages if m['role'] == 'user']
        assistant_msgs = [m for m in st.session_state.messages if m['role'] == 'assistant']
        
        user_word_count = sum(len(m['content']) for m in user_msgs)
        assistant_word_count = sum(len(m['content']) for m in assistant_msgs)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("用户消息", len(user_msgs))
        with col2:
            st.metric("助手回复", len(assistant_msgs))
        with col3:
            st.metric("用户字数", user_word_count)
        with col4:
            st.metric("助手字数", assistant_word_count)
        
        # 对话时间线
        if len(st.session_state.messages) > 1:
            timestamps = []
            roles = []
            
            for msg in st.session_state.messages:
                if 'timestamp' in msg:
                    timestamps.append(msg['timestamp'])
                    roles.append('用户' if msg['role'] == 'user' else '助手')
            
            if timestamps:
                df = pd.DataFrame({
                    'timestamp': pd.to_datetime(timestamps),
                    'role': roles,
                    'count': 1
                })
                
                fig = px.scatter(
                    df, 
                    x='timestamp', 
                    y='role',
                    title='对话时间线',
                    color='role',
                    color_discrete_map={'用户': '#2196f3', '助手': '#9c27b0'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

def main():
    """主函数"""
    init_session_state()
    
    # 侧边栏
    display_sidebar()
    
    # 主界面导航
    tab1, tab2, tab3 = st.tabs(["💬 法律咨询", "🔍 文档搜索", "📋 会话总结"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_search_interface()
    
    with tab3:
        display_summary_interface()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>⚖️ 法律咨询助手 - 基于AI的智能法律咨询系统</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
