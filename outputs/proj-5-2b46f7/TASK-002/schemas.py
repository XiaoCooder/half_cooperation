"""
Pydantic 数据验证模式（完整版）
任务码: TASK-002
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ============== 用户相关模式 ==============

class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户模式"""
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    avatar: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    id: int
    username: str
    nickname: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 分类相关模式 ==============

class CategoryBase(BaseModel):
    """分类基础模式"""
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class CategoryResponse(CategoryBase):
    """分类响应模式"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 标签相关模式 ==============

class TagBase(BaseModel):
    """标签基础模式"""
    name: str = Field(..., min_length=1, max_length=30)
    slug: str = Field(..., min_length=1, max_length=30)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=30)


class TagResponse(TagBase):
    """标签响应模式"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 文章相关模式 ==============

class PostBase(BaseModel):
    """文章基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = Field(None, max_length=255)


class PostCreate(PostBase):
    """创建文章模式"""
    slug: Optional[str] = None
    is_published: bool = False
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []


class PostUpdate(BaseModel):
    """更新文章模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = Field(None, max_length=255)
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class PostListResponse(BaseModel):
    """文章列表响应（精简）"""
    id: int
    title: str
    slug: str
    summary: Optional[str]
    cover_image: Optional[str]
    is_published: bool
    view_count: int
    author: UserListResponse
    category: Optional[CategoryResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class PostResponse(PostBase):
    """文章详情响应"""
    id: int
    slug: str
    is_published: bool
    view_count: int
    author: UserListResponse
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== 分页模式 ==============

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PostListResponse]
