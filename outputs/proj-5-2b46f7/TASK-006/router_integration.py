"""
路由注册示例 - 将管理文章路由和认证路由挂载到 FastAPI 应用
任务码: TASK-006

在 main.py 中添加以下代码:

    from auth import get_current_user
    from posts_admin import router as posts_admin_router
    app.include_router(posts_admin_router)

"""

INTEGRATION_EXAMPLE = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ... 其他导入（TASK-001/002/005）...

# 导入认证和管理路由
from posts_admin import router as posts_admin_router

app = FastAPI(
    title="Personal Blog API",
    description="前后端分离的个人博客系统后端 API",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（注意：管理路由需放在公开路由之后，避免路径冲突）
# app.include_router(posts_router)       # TASK-005: 公开路由
app.include_router(posts_admin_router)  # TASK-006: 管理路由


@app.get("/")
async def root():
    return {"message": "Welcome to Personal Blog API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog-backend"}
'''
