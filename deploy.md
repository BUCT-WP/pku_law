# PKU_LAW 项目配置部署文档

## 项目概述

基于FAISS向量检索和大语言模型的法律咨询问答系统，提供智能法律咨询服务。

## 系统要求

- **操作系统**: macOS, Linux, Windows
- **Python版本**: 3.8+
- **内存**: 推荐 8GB 以上
- **存储**: 至少 2GB 可用空间
- **网络**: 需要访问OpenAI API

## 1. 环境准备

### 1.1 克隆项目

```bash
git clone https://github.com/BUCT-WP/pku_law.git
cd pku_law
```

### 1.2 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 1.3 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 数据准备

### 2.1 法律条文数据

项目包含预处理的法律条文数据：
- `law/` 目录：包含各种法律条文的文本文件
- 数据格式：UTF-8编码的文本文件

### 2.2 构建FAISS索引

首次运行前需要构建向量索引：

```bash
python build_faiss_index.py
```

此步骤将生成：
- `law_index.bin`: FAISS向量索引文件
- `metadata.pkl`: 元数据文件

## 3. 配置设置

### 3.1 环境变量配置

在 `restful/` 目录下创建 `.env` 文件：

```bash
cd restful
touch .env
```

在 `.env` 文件中添加以下配置：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# FAISS索引路径配置
FAISS_INDEX_PATH=law_index.bin
METADATA_PATH=metadata.pkl

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=False

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs
```

### 3.2 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥（必需） | 无 |
| `OPENAI_API_BASE` | OpenAI API基础URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型名称 | `gpt-4` |
| `FAISS_INDEX_PATH` | FAISS索引文件路径 | `law_index.bin` |
| `METADATA_PATH` | 元数据文件路径 | `metadata.pkl` |
| `HOST` | 服务器监听地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |

## 4. 启动系统

### 4.1 一键启动（推荐）

使用提供的启动脚本：

```bash
chmod +x start_system.sh
./start_system.sh
```

### 4.2 手动启动

#### 启动FastAPI后端服务

```bash
cd restful
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动Streamlit前端界面

```bash
# 在另一个终端窗口中
streamlit run streamlit_app.py --server.port 8501
```

### 4.3 停止系统

```bash
chmod +x stop_system.sh
./stop_system.sh
```

## 5. 访问系统

启动成功后，可以通过以下方式访问：

- **Streamlit前端**: http://localhost:8501
- **FastAPI后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 6. 系统验证

### 6.1 检查系统状态

```bash
# 检查FastAPI服务
curl http://localhost:8000/health

# 检查数据文件
python -c "import os; print('FAISS索引:', os.path.exists('law_index.bin')); print('元数据:', os.path.exists('metadata.pkl'))"
```

### 6.2 测试API接口

```bash
# 测试问答接口
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是合同法？", "session_id": "test_session"}'
```

## 7. 常见问题排查

### 7.1 依赖问题

```bash
# 问题：缺少某些依赖
# 解决：重新安装依赖
pip install -r requirements.txt --upgrade
```

### 7.2 FAISS索引问题

```bash
# 问题：索引文件不存在或损坏
# 解决：重新构建索引
python build_faiss_index.py
```

### 7.3 OpenAI API问题

```bash
# 问题：API调用失败
# 解决：检查API密钥和网络连接
python -c "import openai; print('OpenAI配置正常')"
```

### 7.4 端口占用问题

```bash
# 问题：端口被占用
# 解决：查找并结束占用进程
lsof -i :8000
kill -9 <PID>
```

## 8. 日志查看

系统日志存储在 `logs/` 目录中：

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log
```

## 9. 性能优化

### 9.1 内存优化

- 对于大规模数据，建议使用 `faiss-gpu` 替代 `faiss-cpu`
- 适当调整批处理大小

### 9.2 并发优化

- 在生产环境中使用 `gunicorn` 部署FastAPI
- 配置适当的工作进程数量

```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn restful.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 10. 生产部署

### 10.1 Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python build_faiss_index.py

EXPOSE 8000
CMD ["uvicorn", "restful.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.2 Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 11. 监控与维护

### 11.1 系统监控

- 监控API响应时间
- 监控内存使用情况
- 监控错误率

### 11.2 定期维护

- 定期更新法律条文数据
- 重建FAISS索引
- 清理日志文件

## 12. 安全建议

- 不要在代码中硬编码API密钥
- 使用HTTPS协议
- 定期更新依赖包
- 限制API访问频率

---

## 技术支持

如遇到问题，请：
1. 查看系统日志
2. 检查环境配置
3. 参考常见问题排查
4. 联系项目维护者

**项目地址**: https://github.com/BUCT-WP/pku_law
**维护者**: BUCT-WP

---

*最后更新: 2025年7月17日*