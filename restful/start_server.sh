#!/bin/bash

# 启动FastAPI应用的脚本

# 设置工作目录
cd "$(dirname "$0")"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi


# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在，请确保环境变量已正确配置"
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# 启动应用
echo "启动法律咨询API服务..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "ReDoc文档: http://localhost:8000/redoc"
echo "按 Ctrl+C 停止服务"

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
