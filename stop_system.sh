#!/bin/bash

# 停止法律咨询系统

echo "🛑 停止法律咨询系统..."

# 停止FastAPI
if [ -f "logs/fastapi.pid" ]; then
    FASTAPI_PID=$(cat logs/fastapi.pid)
    if kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "🔧 停止FastAPI服务 (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID
        sleep 2
        if kill -0 $FASTAPI_PID 2>/dev/null; then
            echo "强制停止FastAPI..."
            kill -9 $FASTAPI_PID
        fi
    fi
    rm -f logs/fastapi.pid
fi

# 停止Streamlit
if [ -f "logs/streamlit.pid" ]; then
    STREAMLIT_PID=$(cat logs/streamlit.pid)
    if kill -0 $STREAMLIT_PID 2>/dev/null; then
        echo "🌟 停止Streamlit服务 (PID: $STREAMLIT_PID)..."
        kill $STREAMLIT_PID
        sleep 2
        if kill -0 $STREAMLIT_PID 2>/dev/null; then
            echo "强制停止Streamlit..."
            kill -9 $STREAMLIT_PID
        fi
    fi
    rm -f logs/streamlit.pid
fi

# 清理其他可能的进程
echo "🧹 清理其他相关进程..."
pkill -f "uvicorn.*main:app" 2>/dev/null
pkill -f "streamlit.*streamlit_app.py" 2>/dev/null

echo "✅ 法律咨询系统已停止"
