"""
Pydantic 数据验证模式
任务码: TASK-001
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============== 文章相关模式 ==============

class ArticleBase(BaseModel):
    """文章基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)


class ArticleCreate(ArticleBase):
    """创建文章模式"""
    slug: Optional[str] = None
    is_published: bool = True


class ArticleUpdate(BaseModel):
    """更新文章模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None


class ArticleResponse(ArticleBase):
    """文章响应模式"""
    id: int
    slug: str
    author: str
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    id: int
    title: str
    slug: str
    summary: Optional[str]
    author: str
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 用户相关模式 ==============

class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=200)


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 通用响应模式 ==============

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    service: str
