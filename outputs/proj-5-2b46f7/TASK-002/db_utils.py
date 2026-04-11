"""
数据库工具函数
任务码: TASK-002
"""

from contextlib import contextmanager
from typing import Generator, TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal

T = TypeVar('T')


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()


class BaseCRUD(Generic[T]):
    """基础 CRUD 操作类"""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """通过 ID 获取记录"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有记录（分页）"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> T:
        """创建记录"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: T, obj_in: dict) -> T:
        """更新记录"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """删除记录"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def count(self, db: Session) -> int:
        """统计记录数"""
        return db.query(self.model).count()
