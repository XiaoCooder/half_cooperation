"""
文章管理 API 路由（需认证）
任务码: TASK-006
实现: POST /api/posts（创建）、PUT /api/posts/{id}（更新）、DELETE /api/posts/{id}（删除）
"""

import re
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

# 引用前序任务模块
from database import get_db
from models import Post, Tag
from schemas import PostCreate, PostUpdate, PostResponse, PostListResponse
from schemas import UserListResponse, CategoryResponse, TagResponse

# 引用本次任务认证模块
from auth import get_current_admin_user, get_current_user
from models import User


def _slugify(text: str) -> str:
    """简单的 slug 生成：转小写、替换非字母数字为连字符、去除首尾连字符"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-") or "untitled"

router = APIRouter(prefix="/api/posts", tags=["Posts - Admin"])


# ============== 辅助函数（复用 TASK-005 的转换逻辑） ==============

def _to_user_list_response(user: User) -> UserListResponse:
    return UserListResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _to_category_response(cat) -> Optional[CategoryResponse]:
    if cat is None:
        return None
    from schemas import CategoryResponse
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


def _generate_unique_slug(db: Session, base_slug: str) -> str:
    """生成唯一的文章 slug"""
    slug = _slugify(base_slug)
    existing = db.query(Post).filter(Post.slug == slug).first()
    if existing:
        # 添加数字后缀
        counter = 1
        while db.query(Post).filter(Post.slug == f"{slug}-{counter}").first():
            counter += 1
        slug = f"{slug}-{counter}"
    return slug


def _sync_tags(db: Session, post: Post, tag_ids: Optional[List[int]]) -> None:
    """同步文章的标签关联"""
    if tag_ids is None:
        return
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    post.tags = tags


# ============== 管理接口 ==============

@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建文章（需认证）",
)
async def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新文章，仅登录用户可操作"""

    # 生成 slug
    slug = post_in.slug or _generate_unique_slug(db, post_in.title)

    # 构建文章对象
    new_post = Post(
        title=post_in.title,
        slug=slug,
        content=post_in.content,
        summary=post_in.summary,
        cover_image=post_in.cover_image,
        is_published=post_in.is_published,
        author_id=current_user.id,
        category_id=post_in.category_id,
    )

    # 设置发布时间
    if post_in.is_published:
        new_post.published_at = datetime.utcnow()

    db.add(new_post)
    db.flush()

    # 关联标签
    if post_in.tag_ids:
        _sync_tags(db, new_post, post_in.tag_ids)

    db.commit()
    db.refresh(new_post)

    # 预加载关联数据
    db_post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags),
        )
        .filter(Post.id == new_post.id)
        .first()
    )

    return _to_post_response(db_post)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="更新文章（需认证）",
)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新文章，仅作者或管理员可操作"""

    post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags),
        )
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # 权限检查：仅作者或管理员可编辑
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this article",
        )

    # 更新字段
    update_data = post_in.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        if hasattr(post, field):
            setattr(post, field, value)

    # 同步标签
    if post_in.tag_ids is not None:
        _sync_tags(db, post, post_in.tag_ids)

    # 如果从未发布变为已发布，设置发布时间
    if post_in.is_published and not post.published_at:
        post.published_at = datetime.utcnow()

    db.commit()
    db.refresh(post)

    return _to_post_response(post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文章（需认证）",
)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除文章，仅作者或管理员可操作"""

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # 权限检查：仅作者或管理员可删除
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this article",
        )

    db.delete(post)
    db.commit()

    return None
