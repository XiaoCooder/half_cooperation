"""
主应用集成示例
任务码: TASK-003
展示如何将认证模块集成到 FastAPI 主应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============== 导入认证相关模块 ==============
from auth_router import router as auth_router
from database import get_db  # 假设从 TASK-002 的 database.py 导入

# ============== 创建应用 ==============

app = FastAPI(
    title="Personal Blog API",
    description="前后端分离的个人博客系统 - 包含用户认证",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============== CORS 配置 ==============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 注册路由 ==============

app.include_router(auth_router)


# ============== 根路径和健康检查 ==============

@app.get("/")
async def root():
    return {
        "message": "Welcome to Personal Blog API",
        "version": "0.2.0",
        "auth_enabled": True
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog-backend", "auth": "enabled"}


# ============== 启动命令 ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_with_auth:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )