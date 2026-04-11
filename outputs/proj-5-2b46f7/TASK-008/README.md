# 个人博客系统后端

任务码: TASK-008

## 功能概述

本任务整合所有后端路由，配置 CORS 支持前端跨域访问，并提供完整的启动服务测试功能。

## 主要功能

### 1. CORS 配置
- 支持多个前端开发服务器端口
- 支持凭证（cookies, authorization headers）
- 支持所有 HTTP 方法和头

```python
# CORS 允许的 origins
CORS_ORIGINS = [
    "http://localhost:5173",   # Vite
    "http://localhost:3000",   # Create React App
    "http://localhost:8080",   # Vue CLI
]
```

### 2. 路由整合

| 路由 | 前缀 | 说明 |
|------|------|------|
| 认证路由 | `/api/auth/*` | 登录、登出、用户信息 |
| 文章路由 | `/api/posts/*` | 文章 CRUD 操作 |

### 3. 启动服务

```bash
# 方式1: 直接运行
python main.py

# 方式2: 使用启动脚本
python server.py start

# 方式3: 使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 测试

```bash
# 测试模块导入
python server.py imports

# 测试 CORS 和模块
python server.py test
```

## API 端点

### 根路径
- `GET /` - API 信息
- `GET /health` - 健康检查
- `GET /ping` - Ping

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户
- `PATCH /api/auth/me` - 更新用户信息
- `POST /api/auth/refresh` - 刷新 Token
- `GET /api/auth/verify` - 验证 Token

### 文章接口
- `GET /api/posts` - 文章列表
- `GET /api/posts/{slug}` - 文章详情
- `POST /api/posts` - 创建文章（需认证）
- `PUT /api/posts/{id}` - 更新文章（需认证）
- `DELETE /api/posts/{id}` - 删除文章（需认证）

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CORS_ORIGINS` | 额外的 CORS origins（逗号分隔） | - |
| `DATABASE_URL` | 数据库连接 URL | sqlite:///blog.db |

## 访问

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json
- 健康检查: http://localhost:8000/health

## 测试 CORS

```python
import httpx

# 测试预检请求
response = httpx.options(
    "http://localhost:8000/api/auth/login",
    headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization",
    }
)

print(response.headers.get("access-control-allow-origin"))
# 应该输出: http://localhost:5173
```

## 依赖

- fastapi
- uvicorn
- sqlalchemy
- pydantic
- python-jose (JWT)
- passlib (密码哈希)

## 集成说明

本任务整合了以下前序任务的成果：
- TASK-001: FastAPI 项目基础
- TASK-002: 数据库配置与数据模型
- TASK-003: JWT 认证模块
- TASK-004: 认证 API 路由
- TASK-006: 文章管理 API
- TASK-007: Markdown 文件存储