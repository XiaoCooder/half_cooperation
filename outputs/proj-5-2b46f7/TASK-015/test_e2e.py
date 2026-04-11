"""
端到端集成测试
任务码: TASK-015
测试完整流程: 健康检查 -> 登录 -> 创建文章 -> 首页显示 -> 文章详情 -> 更新 -> 删除

使用 FastAPI TestClient，内存 SQLite 数据库。
组装所有前序任务模块到同一应用。
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

# ============== 组装所有前序任务模块 ==============

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

# 添加所有前序任务目录到 sys.path
TASK_PATHS = [
    os.path.join(PROJECT_DIR, "TASK-001"),
    os.path.join(PROJECT_DIR, "TASK-002"),
    os.path.join(PROJECT_DIR, "TASK-003"),
    os.path.join(PROJECT_DIR, "TASK-004"),
    os.path.join(PROJECT_DIR, "TASK-006"),
    os.path.join(PROJECT_DIR, "TASK-007"),
]

for p in TASK_PATHS:
    if p not in sys.path:
        sys.path.insert(0, p)

# ============== 覆盖数据库配置为内存 SQLite ==============

# 在导入 database 模块前设置环境变量/覆盖
# 由于 database.py 使用固定路径，我们需要 monkey-patch
import database as db_module
# 创建内存数据库
db_module.SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
db_module.engine = __import__("sqlalchemy").create_engine(
    db_module.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
db_module.SessionLocal = __import__("sqlalchemy.orm").orm.sessionmaker(
    autocommit=False, autoflush=False, bind=db_module.engine
)

from database import Base, engine, SessionLocal, get_db
from models import User, Post, Category, Tag

# ============== 覆盖 auth.py 中的 settings SECRET_KEY ==============
try:
    import auth as auth_task
    auth_task.settings.SECRET_KEY = "test-secret-key-e2e"
    auth_task.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
except ImportError:
    pass

# ============== 构建测试用 FastAPI 应用 ==============

def create_test_app() -> FastAPI:
    """组装完整的 FastAPI 应用，使用内存数据库"""

    app = FastAPI(
        title="Personal Blog API - E2E Test",
        version="0.5.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        response.headers["X-Process-Time"] = str(elapsed)
        return response

    # 注册认证路由
    try:
        from auth_api import router as auth_router
        app.include_router(auth_router)
    except ImportError as e:
        print(f"⚠️ auth_api 未导入: {e}")

    # 注册文章管理路由
    try:
        from posts_admin import router as posts_admin_router
        app.include_router(posts_admin_router)
    except ImportError as e:
        print(f"⚠️ posts_admin 未导入: {e}")

    # 注册公开文章路由
    try:
        # TASK-005 的路由文件名为 posts.py
        posts_path = os.path.join(PROJECT_DIR, "TASK-005", "posts.py")
        if os.path.exists(posts_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("posts_public", posts_path)
            posts_public_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(posts_public_mod)
            app.include_router(posts_public_mod.router)
    except ImportError as e:
        print(f"⚠️ posts_public 未导入: {e}")

    # 根路径
    @app.get("/")
    async def root():
        return {"message": "Welcome to Personal Blog API", "version": app.version}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "blog-backend"}

    return app


# ============== 全局 fixtures ==============

@pytest.fixture(scope="session")
def app():
    """创建测试应用"""
    return create_test_app()


@pytest.fixture(scope="function")
def db_session():
    """每个测试前重建数据库表并插入种子数据"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # 插入种子数据
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # 创建管理员
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            nickname="管理员",
            is_active=True,
            is_admin=True,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)

        # 创建分类
        tech_cat = Category(name="技术", slug="tech", description="技术文章")
        session.add(tech_cat)
        session.commit()
        session.refresh(tech_cat)

        # 创建标签
        py_tag = Tag(name="Python", slug="python")
        session.add(py_tag)
        session.commit()
        session.refresh(py_tag)

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(app, db_session):
    """创建带测试数据库的 TestClient"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ============== 端到端测试流程 ==============

class TestEndToEnd:
    """完整的端到端流程测试"""

    def test_01_health_check(self, client):
        """步骤 1: 健康检查 - 确认后端服务正常"""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "blog-backend"
        print("\n✅ [E2E 1/7] 健康检查通过")

    def test_02_root_endpoint(self, client):
        """确认根路径返回 API 信息"""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        print("✅ [E2E 2/7] 根路径正常")

    def test_03_login(self, client, db_session):
        """步骤 2: 登录 - 获取 JWT token"""
        resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert resp.status_code == 200, f"登录失败: {resp.text}"
        data = resp.json()

        assert "access_token" in data, "响应缺少 access_token"
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

        # 保存到测试实例供后续使用
        TestEndToEnd.token = data["access_token"]
        print(f"✅ [E2E 3/7] 登录成功, token: {TestEndToEnd.token[:20]}...")

    def test_04_create_post(self, client, db_session):
        """步骤 3: 创建文章 - POST /api/posts"""
        token = TestEndToEnd.token

        resp = client.post(
            "/api/posts",
            json={
                "title": "端到端测试文章",
                "content": "# 这是一篇测试文章\n\n用于验证完整的博客系统流程。",
                "summary": "E2E 测试用文章",
                "is_published": True,
                "slug": "e2e-test-article",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201, f"创建文章失败: {resp.text}"
        data = resp.json()

        assert data["title"] == "端到端测试文章"
        assert data["slug"] == "e2e-test-article"
        assert data["is_published"] is True
        assert data["content"] == "# 这是一篇测试文章\n\n用于验证完整的博客系统流程。"
        assert data["author"]["username"] == "admin"

        TestEndToEnd.post_id = data["id"]
        TestEndToEnd.post_slug = data["slug"]
        print(f"✅ [E2E 4/7] 创建文章成功, id={TestEndToEnd.post_id}, slug={TestEndToEnd.post_slug}")

    def test_05_public_list_shows_post(self, client):
        """步骤 4: 首页文章列表 - 确认新文章出现在公开列表"""
        resp = client.get("/api/posts?page=1&page_size=10")
        assert resp.status_code == 200, f"获取文章列表失败: {resp.text}"
        data = resp.json()

        assert data["total"] >= 1, "文章总数应 >= 1"
        assert data["page"] == 1
        assert "items" in data

        # 找到我们创建的文章
        slugs = [item["slug"] for item in data["items"]]
        assert TestEndToEnd.post_slug in slugs, f"文章 '{TestEndToEnd.post_slug}' 不在列表中"

        # 验证列表项包含必要字段
        post_item = next(p for p in data["items"] if p["slug"] == TestEndToEnd.post_slug)
        assert post_item["title"] == "端到端测试文章"
        assert post_item["is_published"] is True
        assert post_item["author"]["username"] == "admin"

        TestEndToEnd.list_data = data
        print(f"✅ [E2E 5/7] 首页列表显示文章, total={data['total']}")

    def test_06_public_detail(self, client, db_session):
        """步骤 5: 文章详情 - GET /api/posts/{slug}"""
        slug = TestEndToEnd.post_slug

        resp = client.get(f"/api/posts/{slug}")
        assert resp.status_code == 200, f"获取文章详情失败: {resp.text}"
        data = resp.json()

        assert data["slug"] == slug
        assert data["title"] == "端到端测试文章"
        assert data["content"] == "# 这是一篇测试文章\n\n用于验证完整的博客系统流程。"
        assert data["summary"] == "E2E 测试用文章"
        assert data["author"]["username"] == "admin"
        assert data["is_published"] is True

        # 验证浏览次数 +1
        assert data["view_count"] >= 1

        print(f"✅ [E2E 6/7] 文章详情正常, view_count={data['view_count']}")

    def test_07_update_and_delete(self, client, db_session):
        """步骤 6-7: 更新文章 -> 删除文章 -> 验证从列表消失"""
        token = TestEndToEnd.token
        post_id = TestEndToEnd.post_id

        # 6a: 更新文章
        resp = client.put(
            f"/api/posts/{post_id}",
            json={"title": "更新后的标题"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, f"更新文章失败: {resp.text}"
        data = resp.json()
        assert data["title"] == "更新后的标题"
        print("✅ [E2E 7a/7] 更新文章成功")

        # 6b: 验证更新后详情
        resp = client.get(f"/api/posts/{TestEndToEnd.post_slug}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后的标题"
        print("✅ [E2E 7b/7] 更新后的详情正确")

        # 7a: 删除文章
        resp = client.delete(
            f"/api/posts/{post_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204, f"删除文章失败: {resp.text}"
        print("✅ [E2E 7c/7] 删除文章成功 (204)")

        # 7b: 验证文章不在公开列表中
        resp = client.get("/api/posts?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        slugs = [item["slug"] for item in data["items"]]
        assert TestEndToEnd.post_slug not in slugs, "删除后文章不应在列表中"
        print("✅ [E2E 7d/7] 文章已从首页列表消失")

        # 7c: 验证详情 404
        resp = client.get(f"/api/posts/{TestEndToEnd.post_slug}")
        assert resp.status_code == 404, "删除后详情应返回 404"
        print("✅ [E2E 7e/7] 删除后详情返回 404")


# ============== 独立功能测试 ==============

class TestAuthEdgeCases:
    """认证边界情况"""

    def test_login_wrong_password(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "pass"},
        )
        assert resp.status_code == 401

    def test_create_without_auth(self, client):
        resp = client.post(
            "/api/posts",
            json={"title": "No Auth", "content": "x"},
        )
        assert resp.status_code == 401

    def test_create_with_invalid_token(self, client):
        resp = client.post(
            "/api/posts",
            json={"title": "Bad Token", "content": "x"},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_delete_without_auth(self, client, db_session):
        # 先创建一个文章
        admin = db_session.query(User).filter(User.username == "admin").first()
        post = Post(
            title="Temp",
            slug="temp-post",
            content="temp",
            is_published=False,
            author_id=admin.id,
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        resp = client.delete(f"/api/posts/{post.id}")
        assert resp.status_code == 401


class TestPublicPostsEdgeCases:
    """公开文章接口边界情况"""

    def test_list_empty(self, client):
        """无文章时返回空列表"""
        resp = client.get("/api/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_draft_not_in_list(self, client, db_session):
        """未发布文章不应出现在公开列表"""
        admin = db_session.query(User).filter(User.username == "admin").first()
        post = Post(
            title="Draft",
            slug="draft-e2e",
            content="draft content",
            is_published=False,
            author_id=admin.id,
        )
        db_session.add(post)
        db_session.commit()

        resp = client.get("/api/posts")
        assert resp.status_code == 200
        slugs = [p["slug"] for p in resp.json()["items"]]
        assert "draft-e2e" not in slugs

    def test_draft_detail_404(self, client, db_session):
        """未发布文章详情应返回 404"""
        admin = db_session.query(User).filter(User.username == "admin").first()
        post = Post(
            title="Secret",
            slug="secret-draft",
            content="secret",
            is_published=False,
            author_id=admin.id,
        )
        db_session.add(post)
        db_session.commit()

        resp = client.get("/api/posts/secret-draft")
        assert resp.status_code == 404

    def test_nonexistent_slug_404(self, client):
        resp = client.get("/api/posts/does-not-exist")
        assert resp.status_code == 404


class TestPagination:
    """分页功能测试"""

    def test_pagination_params(self, client, db_session):
        """验证分页参数正确生效"""
        admin = db_session.query(User).filter(User.username == "admin").first()
        for i in range(25):
            db_session.add(Post(
                title=f"Post {i}",
                slug=f"pagination-test-{i}",
                content=f"Content {i}",
                is_published=True,
                author_id=admin.id,
            ))
        db_session.commit()

        # 第一页
        resp = client.get("/api/posts?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert len(data["items"]) == 10

        # 第三页
        resp = client.get("/api/posts?page=3&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 3
        assert len(data["items"]) == 5

    def test_invalid_page_params(self, client):
        resp = client.get("/api/posts?page=0")
        assert resp.status_code == 422

        resp = client.get("/api/posts?page_size=0")
        assert resp.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
