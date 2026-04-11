"""
路由注册示例 - 将文章路由挂载到 FastAPI 应用
任务码: TASK-005

在 main.py 中添加以下代码即可注册路由:

    from posts import router as posts_router
    app.include_router(posts_router)

"""

# 完整的 main.py 集成示例（供参考）
INTEGRATION_EXAMPLE = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ... 其他导入 ...

# 导入文章路由
from posts import router as posts_router

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

# 注册路由
app.include_router(posts_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Personal Blog API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog-backend"}
'''
