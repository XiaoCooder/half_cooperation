"""
完整的主应用模块
任务码: TASK-004
整合数据库配置、认证模块，提供可运行的 FastAPI 应用
"""

import sys
import os

# 添加前序任务模块路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK002_PATH = os.path.join(BASE_DIR, "TASK-002")
TASK003_PATH = os.path.join(BASE_DIR, "TASK-003")

sys.path.insert(0, TASK002_PATH)
sys.path.insert(0, TASK003_PATH)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入认证 API 路由
from auth_api import router as auth_router

# 导入数据库初始化
from database import init_db, check_db


# ============== 创建应用 ==============

app = FastAPI(
    title="Personal Blog API",
    description="""
前后端分离的个人博客系统后端 API

## 认证接口
- `/api/auth/login` - 用户登录
- `/api/auth/logout` - 用户登出
- `/api/auth/me` - 获取当前用户信息

## 认证方式
使用 JWT Bearer Token 认证，在请求头添加：
```
Authorization: Bearer <access_token>
```
""",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============== CORS 配置 ==============

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:3000",  # React 默认端口
        "http://localhost:8080",  # Vue 默认端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== 注册路由 ==============

app.include_router(auth_router)


# ============== 启动事件 ==============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("🚀 Starting Personal Blog API...")
    print("📦 Initializing database...")

    # 检查数据库连接
    if check_db():
        print("✅ Database connection successful")
    else:
        print("⚠️ Database connection failed, initializing...")
        init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    print("🛑 Shutting down Personal Blog API...")


# ============== 根路径 ==============

@app.get("/", tags=["root"])
async def root():
    """API 根路径"""
    return {
        "message": "Welcome to Personal Blog API",
        "version": "0.3.0",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "login": "/api/auth/login",
                "logout": "/api/auth/logout",
                "me": "/api/auth/me"
            }
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "blog-backend",
        "version": "0.3.0",
        "database": "connected"
    }


# ============== 启动命令 ==============

if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("Personal Blog Backend Server")
    print("=" * 50)
    print(f"API Docs: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )