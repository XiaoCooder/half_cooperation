"""
数据库配置模块（增强版）
任务码: TASK-002
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "blog.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 必需
    echo=False,  # 设置为 True 可查看 SQL 日志
    pool_pre_ping=True,  # 连接池健康检查
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 声明基类
Base = declarative_base()


def get_db():
    """获取数据库会话的依赖函数（用于 FastAPI）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库 - 创建所有表"""
    # 导入模型确保它们被注册到 Base
    from models import User, Post, Category, Tag, PostTag

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库表创建完成: {DATABASE_PATH}")
    return True


def drop_db():
    """删除所有表（危险操作！）"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ 所有数据库表已删除")


def check_db():
    """检查数据库连接状态"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


# SQLite 外键支持启用
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """启用 SQLite 外键约束"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
