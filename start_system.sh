#!/bin/bash

# 法律咨询系统启动脚本
# 该脚本会同时启动FastAPI后端和Streamlit前端

echo "🚀 启动法律咨询系统..."

# 检查依赖
echo "📦 检查Python依赖..."
python3 -c "import fastapi, streamlit, requests" 2>/dev/null || {
    echo "❌ 缺少必要依赖，请运行: pip install -r requirements.txt"
    exit 1
}

# 检查数据文件
echo "📊 检查数据文件..."
if [ ! -f "law_index.bin" ] || [ ! -f "metadata.pkl" ]; then
    echo "❌ 缺少FAISS索引文件，请先运行 build_faiss_index.py"
    exit 1
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ] && [ ! -f "restful/.env" ]; then
    echo "⚠️  警告: 未检测到OPENAI_API_KEY环境变量或.env文件"
    echo "请确保在 restful/.env 文件中配置了OPENAI_API_KEY"
fi

# 创建日志目录
mkdir -p logs

# 检查端口是否被占用
echo "🔍 检查端口占用情况..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口8000已被占用，尝试停止现有进程..."
    # 尝试从PID文件停止
    if [ -f "logs/fastapi.pid" ]; then
        OLD_PID=$(cat logs/fastapi.pid)
        if kill -0 $OLD_PID 2>/dev/null; then
            kill $OLD_PID
            sleep 2
        fi
        rm -f logs/fastapi.pid
    fi
    # 如果还在占用，强制停止
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🔄 强制停止占用8000端口的进程..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
fi

if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口8501已被占用，尝试停止现有进程..."
    # 尝试从PID文件停止
    if [ -f "logs/streamlit.pid" ]; then
        OLD_PID=$(cat logs/streamlit.pid)
        if kill -0 $OLD_PID 2>/dev/null; then
            kill $OLD_PID
            sleep 2
        fi
        rm -f logs/streamlit.pid
    fi
    # 如果还在占用，强制停止
    if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🔄 强制停止占用8501端口的进程..."
        lsof -ti:8501 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
fi

# 启动FastAPI后端
echo "🔧 启动FastAPI后端服务 (端口: 8000)..."
cd restful
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI PID: $FASTAPI_PID"
cd ..

# 等待FastAPI启动
echo "⏳ 等待FastAPI服务启动..."
sleep 5

# 检查FastAPI是否启动成功
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ FastAPI后端启动成功"
else
    echo "❌ FastAPI后端启动失败，请检查日志: logs/fastapi.log"
    kill $FASTAPI_PID 2>/dev/null
    exit 1
fi

# 启动Streamlit前端
echo "🌟 启动Streamlit前端界面 (端口: 8501)..."
nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false --server.enableCORS false > logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

# 保存进程ID
echo $FASTAPI_PID > logs/fastapi.pid
echo $STREAMLIT_PID > logs/streamlit.pid

echo ""
echo "🎉 法律咨询系统启动完成!"
echo ""
echo "📍 服务地址:"
echo "   - FastAPI后端: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo "   - Streamlit前端: http://localhost:8501"
echo ""
echo "📋 管理命令:"
echo "   - 查看日志: tail -f logs/fastapi.log 或 tail -f logs/streamlit.log"
echo "   - 停止服务: ./stop_system.sh"
echo ""
echo "⏰ 等待Streamlit启动..."
sleep 10

# 检查Streamlit是否启动成功
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Streamlit前端启动成功"
else
    echo "⚠️  Streamlit启动可能需要更多时间，请稍候..."
fi

# 尝试打开浏览器
if command -v open > /dev/null; then
    echo "🌐 正在打开浏览器..."
    open http://localhost:8501
elif command -v xdg-open > /dev/null; then
    echo "🌐 正在打开浏览器..."
    xdg-open http://localhost:8501
else
    echo "🌐 请手动打开浏览器访问: http://localhost:8501"
fi

echo ""
echo "✨ 系统运行中，按 Ctrl+C 停止所有服务"
echo ""

# 信号处理函数 - 当收到中断信号时停止所有服务
cleanup() {
    echo ""
    echo "🛑 收到停止信号，正在关闭服务..."
    
    # 停止FastAPI
    if [ ! -z "$FASTAPI_PID" ] && kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "🔧 停止FastAPI服务 (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID
        wait $FASTAPI_PID 2>/dev/null
    fi
    
    # 停止Streamlit
    if [ ! -z "$STREAMLIT_PID" ] && kill -0 $STREAMLIT_PID 2>/dev/null; then
        echo "🌟 停止Streamlit服务 (PID: $STREAMLIT_PID)..."
        kill $STREAMLIT_PID
        wait $STREAMLIT_PID 2>/dev/null
    fi
    
    # 清理PID文件
    rm -f logs/fastapi.pid logs/streamlit.pid
    
    echo "✅ 所有服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 监控进程
while true; do
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "❌ FastAPI进程意外停止"
        break
    fi
    
    if ! kill -0 $STREAMLIT_PID 2>/dev/null; then
        echo "❌ Streamlit进程意外停止"
        break
    fi
    
    sleep 5
done

echo "🛑 检测到服务异常停止，退出监控"
cleanup
