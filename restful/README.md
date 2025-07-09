# 法律咨询API RESTful接口

基于FastAPI开发的法律咨询系统RESTful API，提供法律文档检索和智能问答服务。

## 功能特性

- 🔍 **法律文档检索**: 基于FAISS的快速相似性搜索
- 🤖 **智能问答**: 结合LLM的法律咨询服务
- 💬 **会话管理**: 支持多会话上下文管理
- 📊 **对话总结**: 自动生成会话摘要
- 🌐 **RESTful API**: 标准的REST接口设计
- 📖 **自动文档**: 集成Swagger UI文档

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的API密钥
nano .env
```

### 3. 启动服务

#### 方式一：使用启动脚本
```bash
chmod +x start_server.sh
./start_server.sh
```

#### 方式二：直接运行
```bash
cd restful
python main.py
```

#### 方式三：使用uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## API接口文档

### 基础接口

#### 1. 健康检查
```http
GET /health
```
**响应示例:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

#### 2. 根路径
```http
GET /
```

### 法律咨询接口

#### 1. 法律咨询查询
```http
POST /query
Content-Type: application/json

{
  "question": "如果我在工作中受伤了，有哪些法律权利和保障？",
  "session_id": "optional-session-id",
  "show_results": true
}
```

**响应示例:**
```json
{
  "answer": "根据相关法律规定...",
  "session_id": "uuid-session-id",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "question": "如果我在工作中受伤了，有哪些法律权利和保障？"
}
```

#### 2. 搜索法律文档
```http
POST /search
Content-Type: application/json

{
  "query": "工伤保障",
  "k": 5
}
```

**响应示例:**
```json
{
  "results": [
    {
      "content": "法条内容...",
      "filename": "中华人民共和国工伤保险条例.txt",
      "score": 0.95,
      "distance": 0.05
    }
  ],
  "total": 5,
  "query": "工伤保障",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 会话管理接口

#### 1. 获取会话总结
```http
GET /sessions/{session_id}/summary
```

#### 2. 删除会话
```http
DELETE /sessions/{session_id}
```

#### 3. 列出所有会话
```http
GET /sessions
```

#### 4. 重置会话
```http
POST /sessions/{session_id}/reset
```

## 客户端示例

### Python客户端

```python
from client_example import LegalConsultationClient

# 创建客户端
client = LegalConsultationClient("http://localhost:8000")

# 健康检查
health = client.health_check()
print(f"服务状态: {health['status']}")

# 法律咨询
response = client.query_law("劳动合同相关问题")
print(f"回答: {response['answer']}")

# 搜索法律文档
results = client.search_laws("劳动法", k=3)
print(f"找到 {results['total']} 条相关法条")
```

### JavaScript客户端

```javascript
const API_BASE_URL = 'http://localhost:8000';

// 法律咨询查询
async function queryLaw(question) {
    const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            show_results: true
        })
    });
    return await response.json();
}

// 搜索法律文档
async function searchLaws(query, k = 5) {
    const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            k: k
        })
    });
    return await response.json();
}
```

### cURL示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/health"

# 法律咨询查询
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "劳动合同相关问题", "show_results": true}'

# 搜索法律文档
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "劳动法", "k": 3}'
```

## 错误处理

API使用标准的HTTP状态码：

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

错误响应格式：
```json
{
  "error": "错误信息",
  "detail": "详细信息",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 配置选项

在 `config.py` 中可以配置：

- API基本信息
- 服务器配置
- CORS设置
- 日志级别
- 会话管理选项
- 检索配置

## 部署指南

### 使用Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 许可证

本项目采用MIT许可证。
