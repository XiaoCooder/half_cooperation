"""
文章管理 API（需认证）的单元测试
任务码: TASK-006
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from database import Base, get_db
from models import User, Post, Category, Tag
from posts_admin import router
from auth import create_access_token

from fastapi import FastAPI


# 测试用内存 SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 覆盖 auth.py 中的 settings，避免密钥不一致
import auth as _auth_module
_auth_module.settings.SECRET_KEY = "test-secret-key"
_auth_module.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
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
def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="hashed_pw",
        nickname="Admin",
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    user = User(
        username="writer",
        email="writer@example.com",
        hashed_password="hashed_pw",
        nickname="Writer",
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": admin_user.id})


@pytest.fixture
def writer_token(regular_user):
    return create_access_token(data={"sub": regular_user.id})


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
def existing_post(db_session, admin_user, sample_category):
    post = Post(
        title="Existing Article",
        slug="existing-article",
        content="Content here",
        summary="A summary",
        is_published=True,
        author_id=admin_user.id,
        category_id=sample_category.id,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ============== 测试: POST /api/posts ==============

class TestCreatePost:
    def test_create_post_success(self, client, admin_token):
        resp = client.post(
            "/api/posts",
            json={
                "title": "New Post",
                "content": "Hello world",
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "New Post"
        assert data["slug"] == "new-post"
        assert data["author"]["username"] == "admin"
        assert data["is_published"] is False

    def test_create_post_with_custom_slug(self, client, admin_token):
        resp = client.post(
            "/api/posts",
            json={
                "title": "Custom",
                "content": "Content",
                "slug": "my-custom-slug",
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 201
        assert resp.json()["slug"] == "my-custom-slug"

    def test_create_post_publish(self, client, admin_token, sample_category, sample_tag):
        resp = client.post(
            "/api/posts",
            json={
                "title": "Published",
                "content": "Content",
                "is_published": True,
                "category_id": sample_category.id,
                "tag_ids": [sample_tag.id],
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_published"] is True
        assert data["category"]["slug"] == "tech"
        assert len(data["tags"]) == 1
        assert data["tags"][0]["slug"] == "python"
        assert data["published_at"] is not None

    def test_create_unauthorized(self, client):
        resp = client.post(
            "/api/posts",
            json={"title": "No Auth", "content": "x"},
        )
        assert resp.status_code == 401


# ============== 测试: PUT /api/posts/{id} ==============

class TestUpdatePost:
    def test_update_own_post(self, client, admin_token, existing_post):
        resp = client.put(
            f"/api/posts/{existing_post.id}",
            json={"title": "Updated Title"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_update_title_and_content(self, client, admin_token, existing_post):
        resp = client.put(
            f"/api/posts/{existing_post.id}",
            json={"title": "New Title", "content": "New content"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "New Title"
        assert data["content"] == "New content"

    def test_update_not_owner_forbidden(self, client, writer_token, existing_post):
        """非作者且非管理员不能编辑"""
        resp = client.put(
            f"/api/posts/{existing_post.id}",
            json={"title": "Hacked"},
            headers=auth_header(writer_token),
        )
        assert resp.status_code == 403

    def test_update_not_found(self, client, admin_token):
        resp = client.put(
            "/api/posts/99999",
            json={"title": "Nope"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_update_unauthorized(self, client, existing_post):
        resp = client.put(
            f"/api/posts/{existing_post.id}",
            json={"title": "No Auth"},
        )
        assert resp.status_code == 401


# ============== 测试: DELETE /api/posts/{id} ==============

class TestDeletePost:
    def test_delete_own_post(self, client, admin_token, existing_post, db_session):
        resp = client.delete(
            f"/api/posts/{existing_post.id}",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 204

        deleted = db_session.query(Post).filter(Post.id == existing_post.id).first()
        assert deleted is None

    def test_delete_not_owner_forbidden(self, client, writer_token, existing_post):
        resp = client.delete(
            f"/api/posts/{existing_post.id}",
            headers=auth_header(writer_token),
        )
        assert resp.status_code == 403

    def test_delete_not_found(self, client, admin_token):
        resp = client.delete(
            "/api/posts/99999",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_delete_unauthorized(self, client, existing_post):
        resp = client.delete(f"/api/posts/{existing_post.id}")
        assert resp.status_code == 401


# ============== 测试: Auth 模块 ==============

class TestAuth:
    def test_create_and_decode_token(self, admin_user):
        token = create_access_token(data={"sub": admin_user.id})
        payload = _auth_module.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == admin_user.id

    def test_decode_invalid_token(self):
        payload = _auth_module.decode_access_token("invalid.token.here")
        assert payload is None

    def test_get_password_hash_and_verify(self):
        from auth import get_password_hash, verify_password
        hashed = get_password_hash("mypassword")
        assert verify_password("mypassword", hashed)
        assert not verify_password("wrongpassword", hashed)
