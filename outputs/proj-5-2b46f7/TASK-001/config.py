"""
应用配置模块
任务码: TASK-001
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 应用信息
    APP_NAME: str = "Personal Blog API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./blog.db"

    # CORS 配置
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


# 全局配置实例
settings = Settings()
