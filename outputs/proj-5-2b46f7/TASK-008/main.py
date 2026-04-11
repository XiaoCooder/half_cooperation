"""
个人博客系统 - 主应用入口
任务码: TASK-008
整合所有路由、配置 CORS、启动服务测试
"""

import sys
import os

# ============== 路径配置 ==============
# 添加前序任务模块路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

# 前序任务目录路径
TASK001_PATH = os.path.join(BASE_DIR, "TASK-001")
TASK002_PATH = os.path.join(BASE_DIR, "TASK-002")
TASK003_PATH = os.path.join(BASE_DIR, "TASK-003")
TASK004_PATH = os.path.join(BASE_DIR, "TASK-004")
TASK006_PATH = os.path.join(BASE_DIR, "TASK-006")
TASK007_PATH = os.path.join(BASE_DIR, "TASK-007")

# 添加到 sys.path
for path in [TASK001_PATH, TASK002_PATH, TASK003_PATH, TASK004_PATH, TASK006_PATH, TASK007_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# ============== 数据库初始化 ==============
try:
    from database import init_db, check_db
    DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 数据库模块导入失败: {e}")
    DB_AVAILABLE = False

# ============== 认证路由 ==============
try:
    from auth_api import router as auth_router
    AUTH_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 认证路由导入失败: {e}")
    AUTH_ROUTER_AVAILABLE = False
    auth_router = None

# ============== 文章管理路由 ==============
try:
    from posts_admin import router as posts_admin_router
    POSTS_ADMIN_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 文章管理路由导入失败: {e}")
    POSTS_ADMIN_ROUTER_AVAILABLE = False
    posts_admin_router = None


# ============== 创建 FastAPI 应用 ==============

app = FastAPI(
    title="Personal Blog API",
    description="""
## 前后端分离博客系统后端 API

### 功能模块
- **认证接口**: 登录、登出、用户信息
- **文章接口**: 创建、读取、更新、删除文章
- **分类标签**: 分类和标签管理

### 认证方式
使用 JWT Bearer Token 认证，在请求头添加：
```
Authorization: Bearer <access_token>
```
""",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============== CORS 配置 ==============

# 允许的前端 origins（可根据环境变量扩展）
CORS_ORIGINS = [
    "http://localhost:5173",   # Vite (React/Vue)
    "http://localhost:3000",    # Create React App
    "http://localhost:8080",    # Vue CLI
    "http://localhost:8000",    # 本地后端
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# 从环境变量添加额外 origins
extra_origins = os.environ.get("CORS_ORIGINS", "")
if extra_origins:
    CORS_ORIGINS.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== 请求日志中间件 ==============

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算耗时
    process_time = time.time() - start_time

    # 打印日志
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    # 添加自定义头
    response.headers["X-Process-Time"] = str(process_time)

    return response


# ============== 注册路由 ==============

# 认证路由
if AUTH_ROUTER_AVAILABLE and auth_router:
    app.include_router(auth_router)
    print("✅ 认证路由已注册: /api/auth/*")
else:
    print("⚠️ 认证路由未注册")

# 文章管理路由
if POSTS_ADMIN_ROUTER_AVAILABLE and posts_admin_router:
    app.include_router(posts_admin_router)
    print("✅ 文章管理路由已注册: /api/posts/*")
else:
    print("⚠️ 文章管理路由未注册")


# ============== 启动事件 ==============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("=" * 60)
    print("🚀 Personal Blog API Starting...")
    print("=" * 60)

    # 初始化数据库
    if DB_AVAILABLE:
        print("📦 Initializing database...")
        if check_db():
            print("✅ Database connection successful")
        else:
            print("⚠️ Database connection failed, attempting to initialize...")
            try:
                init_db()
                print("✅ Database initialized")
            except Exception as e:
                print(f"❌ Database initialization failed: {e}")

    # 显示注册的路由
    print("\n📋 Registered Routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            methods = ",".join(route.methods) if route.methods else "GET"
            print(f"   {methods:8} {route.path}")

    print("=" * 60)
    print("✅ Server ready!")
    print("📖 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc:    http://localhost:8000/redoc")
    print("=" * 60)


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
        "version": app.version,
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "login": "POST /api/auth/login",
                "logout": "POST /api/auth/logout",
                "me": "GET /api/auth/me",
                "refresh": "POST /api/auth/refresh",
            },
            "posts": {
                "list": "GET /api/posts",
                "get": "GET /api/posts/{slug}",
                "create": "POST /api/posts",
                "update": "PUT /api/posts/{id}",
                "delete": "DELETE /api/posts/{id}",
            }
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查接口"""
    db_status = "connected" if (DB_AVAILABLE and check_db()) else "disconnected"

    return {
        "status": "healthy",
        "service": "blog-backend",
        "version": app.version,
        "database": db_status,
        "routers": {
            "auth": AUTH_ROUTER_AVAILABLE,
            "posts_admin": POSTS_ADMIN_ROUTER_AVAILABLE,
        }
    }


@app.get("/ping", tags=["health"])
async def ping():
    """简单 ping 接口"""
    return {"message": "pong"}


# ============== 启动命令 ==============

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Personal Blog Backend Server")
    print("=" * 60)
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )