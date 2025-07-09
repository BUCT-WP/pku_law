from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import sys
from datetime import datetime
import uuid
import logging

# 添加父目录到系统路径，以便导入agent模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import LegalConsultationSystem, ConversationContext
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def verify_data_files():
    """验证数据文件是否存在，并返回绝对路径"""
    # 获取项目根目录（restful目录的父目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 从环境变量获取相对路径
    faiss_index_relative = os.getenv("FAISS_INDEX_PATH", "law_index.bin")
    metadata_relative = os.getenv("METADATA_PATH", "metadata.pkl")
    
    # 构建绝对路径
    faiss_index_path = os.path.join(project_root, faiss_index_relative)
    metadata_path = os.path.join(project_root, metadata_relative)
    
    # 验证文件是否存在
    if not os.path.exists(faiss_index_path):
        raise FileNotFoundError(f"FAISS index file not found: {faiss_index_path}")
    
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    return faiss_index_path, metadata_path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="法律咨询API",
    description="基于FAISS检索和LLM的法律咨询系统RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储咨询系统实例
consultation_system = None

def get_consultation_system():
    """获取咨询系统实例"""
    global consultation_system
    if consultation_system is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        try:
            # 验证数据文件是否存在
            index_path, metadata_path = verify_data_files()
            logger.info(f"Using FAISS index: {index_path}")
            logger.info(f"Using metadata: {metadata_path}")
            
            consultation_system = LegalConsultationSystem(
                openai_api_key=api_key,
                index_path=index_path,
                metadata_path=metadata_path
            )
        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Required data files not found: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize consultation system: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize consultation system: {str(e)}"
            )
    
    return consultation_system

# Pydantic模型定义
class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str = Field(..., description="法律咨询问题", min_length=1)
    session_id: Optional[str] = Field(None, description="会话ID")
    show_results: bool = Field(True, description="是否展示检索结果")

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索查询", min_length=1)
    k: int = Field(5, description="返回结果数量", ge=1, le=20)

class SessionRequest(BaseModel):
    """会话请求模型"""
    session_id: str = Field(..., description="会话ID")

class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str = Field(..., description="法律建议")
    session_id: str = Field(..., description="会话ID")
    timestamp: str = Field(..., description="响应时间")
    question: str = Field(..., description="原始问题")

class SearchResult(BaseModel):
    """搜索结果模型"""
    content: str = Field(..., description="法条内容")
    filename: str = Field(..., description="文件名")
    score: float = Field(..., description="相关度评分")
    distance: float = Field(..., description="距离值")

class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[SearchResult] = Field(..., description="搜索结果列表")
    total: int = Field(..., description="结果总数")
    query: str = Field(..., description="搜索查询")
    timestamp: str = Field(..., description="搜索时间")

class SummaryResponse(BaseModel):
    """总结响应模型"""
    summary: str = Field(..., description="对话总结")
    session_id: str = Field(..., description="会话ID")
    timestamp: str = Field(..., description="总结时间")

class StatusResponse(BaseModel):
    """状态响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="API版本")
    timestamp: str = Field(..., description="当前时间")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")
    timestamp: str = Field(..., description="错误时间")

# 会话管理
sessions: Dict[str, ConversationContext] = {}

@app.get("/", response_model=StatusResponse)
async def root():
    """根路径 - 返回API状态"""
    return StatusResponse(
        status="active",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=StatusResponse)
async def health_check():
    """健康检查"""
    try:
        # 尝试初始化咨询系统来验证配置
        system = get_consultation_system()
        return StatusResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse)
async def query_law(request: QueryRequest):
    """法律咨询查询"""
    try:
        system = get_consultation_system()
        
        # 生成或使用现有会话ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # 恢复或创建会话上下文
        if session_id in sessions:
            system.context = sessions[session_id]
        else:
            system.reset_context()
            system.context.session_id = session_id
        
        # 处理查询
        logger.info(f"Processing query for session {session_id}: {request.question}")
        answer = system.process_query_with_display(
            request.question, 
            show_results=request.show_results
        )
        
        # 保存会话上下文
        sessions[session_id] = system.context
        
        return QueryResponse(
            answer=answer,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            question=request.question
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.post("/search", response_model=SearchResponse)
async def search_laws(request: SearchRequest):
    """搜索法律文档"""
    try:
        system = get_consultation_system()
        
        logger.info(f"Searching for: {request.query}")
        results = system.search_and_display(request.query, k=request.k)
        
        # 转换结果格式
        search_results = [
            SearchResult(
                content=result['content'],
                filename=result['filename'],
                score=result['score'],
                distance=result['distance']
            )
            for result in results
        ]
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query=request.query,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/sessions/{session_id}/summary", response_model=SummaryResponse)
async def get_session_summary(session_id: str):
    """获取会话总结"""
    try:
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        system = get_consultation_system()
        system.context = sessions[session_id]
        
        logger.info(f"Getting summary for session {session_id}")
        summary = system.get_conversation_summary()
        
        return SummaryResponse(
            summary=summary,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {str(e)}"
        )

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        del sessions[session_id]
        logger.info(f"Deleted session {session_id}")
        
        return {"message": "Session deleted successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session deletion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session deletion failed: {str(e)}"
        )

@app.get("/sessions")
async def list_sessions():
    """列出所有活跃会话"""
    try:
        session_info = []
        for session_id, context in sessions.items():
            session_info.append({
                "session_id": session_id,
                "message_count": len(context.history),
                "last_activity": context.history[-1]['timestamp'] if context.history else None,
                "current_topic": context.current_topic
            })
        
        return {
            "sessions": session_info,
            "total": len(session_info),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Session listing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session listing failed: {str(e)}"
        )

@app.post("/sessions/{session_id}/reset")
async def reset_session(session_id: str):
    """重置会话"""
    try:
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # 重置会话上下文
        sessions[session_id] = ConversationContext()
        sessions[session_id].session_id = session_id
        
        logger.info(f"Reset session {session_id}")
        
        return {"message": "Session reset successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session reset failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session reset failed: {str(e)}"
        )

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
