"""
数据库种子数据
任务码: TASK-002
用于填充测试数据
"""

from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import User, Post, Category, Tag
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def seed_categories(db: Session):
    """创建默认分类"""
    categories = [
        Category(name="技术", slug="tech", description="技术文章与编程心得"),
        Category(name="生活", slug="life", description="日常生活记录"),
        Category(name="随笔", slug="essay", description="随想与感悟"),
        Category(name="教程", slug="tutorial", description="教程与指南"),
    ]
    for cat in categories:
        existing = db.query(Category).filter(Category.slug == cat.slug).first()
        if not existing:
            db.add(cat)
    db.commit()
    print("✅ 分类数据已创建")


def seed_tags(db: Session):
    """创建默认标签"""
    tags = [
        Tag(name="Python", slug="python"),
        Tag(name="FastAPI", slug="fastapi"),
        Tag(name="JavaScript", slug="javascript"),
        Tag(name="Vue", slug="vue"),
        Tag(name="数据库", slug="database"),
        Tag(name="前端", slug="frontend"),
        Tag(name="后端", slug="backend"),
    ]
    for tag in tags:
        existing = db.query(Tag).filter(Tag.slug == tag.slug).first()
        if not existing:
            db.add(tag)
    db.commit()
    print("✅ 标签数据已创建")


def seed_users(db: Session):
    """创建测试用户"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        nickname="管理员",
        bio="博客管理员",
        is_active=True,
        is_admin=True,
    )
    user1 = User(
        username="alice",
        email="alice@example.com",
        hashed_password=get_password_hash("alice123"),
        nickname="Alice",
        bio="热爱编程的设计师",
        is_active=True,
        is_admin=False,
    )

    for u in [admin, user1]:
        existing = db.query(User).filter(User.username == u.username).first()
        if not existing:
            db.add(u)
    db.commit()
    print("✅ 用户数据已创建")
    return admin, user1


def seed_posts(db: Session, admin: User):
    """创建测试文章"""
    tech_cat = db.query(Category).filter(Category.slug == "tech").first()
    python_tag = db.query(Tag).filter(Tag.slug == "python").first()
    fastapi_tag = db.query(Tag).filter(Tag.slug == "fastapi").first()

    posts = [
        Post(
            title="欢迎使用个人博客系统",
            slug="welcome-to-blog",
            content="""
# 欢迎使用个人博客系统

这是一篇示例文章，展示了博客系统的基本功能。

## 特性

- 📝 Markdown 支持
- 🏷️ 标签分类
- 👤 用户管理
- 🎨 响应式设计

开始创作吧！
            """.strip(),
            summary="个人博客系统的第一篇示例文章",
            is_published=True,
            view_count=42,
            author_id=admin.id,
            category_id=tech_cat.id if tech_cat else None,
            published_at=datetime.now(),
        ),
        Post(
            title="FastAPI 入门指南",
            slug="fastapi-getting-started",
            content="""
# FastAPI 入门指南

FastAPI 是一个现代、快速的 Web 框架。

## 安装

```bash
pip install fastapi uvicorn
```

## 快速开始

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```
            """.strip(),
            summary="FastAPI 框架的基础入门教程",
            is_published=True,
            view_count=128,
            author_id=admin.id,
            category_id=tech_cat.id if tech_cat else None,
            published_at=datetime.now(),
        ),
    ]

    # 关联标签
    if python_tag:
        posts[1].tags.append(python_tag)
    if fastapi_tag:
        posts[1].tags.append(fastapi_tag)

    for post in posts:
        existing = db.query(Post).filter(Post.slug == post.slug).first()
        if not existing:
            db.add(post)
    db.commit()
    print("✅ 文章数据已创建")


def seed_all():
    """填充所有种子数据"""
    db = SessionLocal()
    try:
        print("\n🌱 开始填充种子数据...")
        print("-" * 40)

        seed_categories(db)
        seed_tags(db)
        admin, user1 = seed_users(db)
        seed_posts(db, admin)

        print("-" * 40)
        print("✅ 所有种子数据填充完成!")
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 先初始化数据库
    init_db()
    # 填充种子数据
    seed_all()
