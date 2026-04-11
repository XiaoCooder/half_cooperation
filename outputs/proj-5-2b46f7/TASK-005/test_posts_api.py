"""
公开文章 API 路由的单元测试
任务码: TASK-005
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 使用内存 SQLite 做测试
from database import Base, get_db
from models import User, Post, Category, Tag
from posts import router

from fastapi import FastAPI


# 测试用数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """每个测试前重建数据库表"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建带测试数据库的 FastAPI 测试客户端"""
    app = FastAPI()
    app.include_router(router)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def sample_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw",
        nickname="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_category(db_session):
    cat = Category(name="Tech", slug="tech", description="技术文章")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture
def sample_tag(db_session):
    tag = Tag(name="Python", slug="python")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture
def published_post(db_session, sample_user, sample_category, sample_tag):
    post = Post(
        title="Hello World",
        slug="hello-world",
        content="This is the content.",
        summary="A summary",
        is_published=True,
        author_id=sample_user.id,
        category_id=sample_category.id,
    )
    post.tags.append(sample_tag)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def draft_post(db_session, sample_user):
    post = Post(
        title="Draft",
        slug="draft-post",
        content="Draft content.",
        is_published=False,
        author_id=sample_user.id,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


# ============== 测试: GET /api/posts ==============

class TestListPosts:
    def test_list_empty(self, client):
        resp = client.get("/api/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_published_only(self, client, published_post, draft_post):
        resp = client.get("/api/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["slug"] == "hello-world"

    def test_pagination(self, client, db_session, sample_user):
        for i in range(15):
            db_session.add(Post(
                title=f"Post {i}",
                slug=f"post-{i}",
                content=f"Content {i}",
                is_published=True,
                author_id=sample_user.id,
            ))
        db_session.commit()

        resp = client.get("/api/posts?page=1&page_size=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total_pages"] == 3
        assert len(data["items"]) == 5

    def test_filter_by_category(self, client, published_post):
        resp = client.get("/api/posts?category=tech")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/api/posts?category=nonexistent")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_filter_by_tag(self, client, published_post):
        resp = client.get("/api/posts?tag=python")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_items_have_author_and_category(self, client, published_post):
        resp = client.get("/api/posts")
        assert resp.status_code == 200
        item = resp.json()["items"][0]
        assert item["author"]["username"] == "testuser"
        assert item["category"]["slug"] == "tech"


# ============== 测试: GET /api/posts/{slug} ==============

class TestGetPost:
    def test_get_by_slug(self, client, published_post):
        resp = client.get("/api/posts/hello-world")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "hello-world"
        assert data["title"] == "Hello World"
        assert data["content"] == "This is the content."

    def test_not_found(self, client):
        resp = client.get("/api/posts/nonexistent")
        assert resp.status_code == 404

    def test_draft_not_found(self, client, draft_post):
        """未发布文章应返回 404"""
        resp = client.get("/api/posts/draft-post")
        assert resp.status_code == 404

    def test_includes_tags(self, client, published_post):
        resp = client.get("/api/posts/hello-world")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["slug"] == "python"

    def test_view_count_increases(self, client, db_session, published_post):
        initial_count = published_post.view_count

        client.get("/api/posts/hello-world")
        db_session.refresh(published_post)
        assert published_post.view_count == initial_count + 1

        client.get("/api/posts/hello-world")
        db_session.refresh(published_post)
        assert published_post.view_count == initial_count + 2
