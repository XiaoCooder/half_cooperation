"""
Personal Blog Backend - FastAPI Application
任务码: TASK-001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Personal Blog API",
    description="前后端分离的个人博客系统后端 API",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Personal Blog API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
