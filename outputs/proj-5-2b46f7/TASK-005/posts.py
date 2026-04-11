"""
公开文章 API 路由
任务码: TASK-005
实现: GET /api/posts（列表，分页）、GET /api/posts/{slug}（详情）
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime

# 引用前序任务模块（TASK-001 / TASK-002）
from database import get_db
from models import Post, User, Category, Tag
from schemas import (
    PostListResponse,
    PostResponse,
    PaginatedResponse,
    UserListResponse,
    CategoryResponse,
    TagResponse,
)

router = APIRouter(prefix="/api/posts", tags=["Posts - Public"])


# ============== 辅助函数 ==============

def _to_user_list_response(user: User) -> UserListResponse:
    return UserListResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _to_category_response(cat: Category) -> CategoryResponse:
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        description=cat.description,
        created_at=cat.created_at,
    )


def _to_tag_response(tag: Tag) -> TagResponse:
    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
        created_at=tag.created_at,
    )


def _to_post_list_response(post: Post) -> PostListResponse:
    category = _to_category_response(post.category) if post.category else None
    return PostListResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        cover_image=post.cover_image,
        is_published=post.is_published,
        view_count=post.view_count,
        author=_to_user_list_response(post.author),
        category=category,
        created_at=post.created_at,
    )


def _to_post_response(post: Post) -> PostResponse:
    category = _to_category_response(post.category) if post.category else None
    tags = [_to_tag_response(t) for t in post.tags]
    return PostResponse(
        id=post.id,
        slug=post.slug,
        title=post.title,
        content=post.content,
        summary=post.summary,
        cover_image=post.cover_image,
        is_published=post.is_published,
        view_count=post.view_count,
        author=_to_user_list_response(post.author),
        category=category,
        tags=tags,
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at,
    )


def _calc_total_pages(total: int, page_size: int) -> int:
    if total == 0:
        return 0
    return (total + page_size - 1) // page_size


# ============== 公开接口 ==============

@router.get("", response_model=PaginatedResponse, summary="获取已发布文章列表")
async def list_posts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    category: Optional[str] = Query(None, description="按分类 slug 筛选"),
    tag: Optional[str] = Query(None, description="按标签 slug 筛选"),
    db: Session = Depends(get_db),
):
    """获取已发布文章列表（分页），可选按分类或标签筛选"""

    base_query = db.query(Post).filter(Post.is_published == True)

    # 分类筛选
    if category:
        base_query = base_query.join(Category).filter(Category.slug == category)

    # 标签筛选
    if tag:
        base_query = base_query.join(Post.tags).filter(Tag.slug == tag)

    # 总数
    total = base_query.count()
    total_pages = _calc_total_pages(total, page_size)

    # 分页查询 + 预加载关联
    skip = (page - 1) * page_size
    posts = (
        base_query
        .options(
            joinedload(Post.author),
            joinedload(Post.category),
        )
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    items = [_to_post_list_response(p) for p in posts]

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items,
    )


@router.get("/{slug}", response_model=PostResponse, summary="获取文章详情")
async def get_post(
    slug: str,
    db: Session = Depends(get_db),
):
    """通过 slug 获取已发布文章详情，并增加浏览次数"""

    post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags),
        )
        .filter(Post.slug == slug)
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Article not found")

    if not post.is_published:
        raise HTTPException(status_code=404, detail="Article not found")

    # 浏览次数 +1
    post.view_count += 1
    db.commit()

    return _to_post_response(post)
