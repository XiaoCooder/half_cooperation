"""
端到端测试 - 独立运行脚本（无需 pytest）
任务码: TASK-015
运行方式: python e2e_runner.py

测试流程:
  1. 健康检查
  2. 登录获取 token
  3. 创建文章
  4. 验证首页列表显示
  5. 验证文章详情
  6. 更新文章
  7. 删除文章并验证消失
"""

import sys
import os
import json

# ============== 组装模块路径 ==============

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

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

# ============== 内存数据库 ==============

import database as db_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_module.SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
db_module.engine = create_engine(
    db_module.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
db_module.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=db_module.engine
)

from database import Base, SessionLocal, get_db
from models import User, Category, Tag, Post
from passlib.context import CryptContext

# 覆盖 auth secret
try:
    import auth as auth_mod
    auth_mod.settings.SECRET_KEY = "test-secret-e2e"
    auth_mod.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
except ImportError:
    pass

# ============== 构建应用 ==============

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
import time

def build_app():
    app = FastAPI(title="Blog E2E Test", version="0.5.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time() - start)
        return response

    try:
        from auth_api import router as auth_router
        app.include_router(auth_router)
    except ImportError as e:
        print(f"⚠️ auth_api: {e}")

    try:
        from posts_admin import router as posts_admin_router
        app.include_router(posts_admin_router)
    except ImportError as e:
        print(f"⚠️ posts_admin: {e}")

    # 公开文章路由
    posts_public_path = os.path.join(PROJECT_DIR, "TASK-005", "posts.py")
    if os.path.exists(posts_public_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("posts_public", posts_public_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        app.include_router(mod.router)

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


# ============== 测试运行器 ==============

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def passed(label):
    print(f"  {Colors.GREEN}✅ PASS{Colors.RESET}  {label}")

def failed(label, detail=""):
    print(f"  {Colors.RED}❌ FAIL{Colors.RESET}  {label}")
    if detail:
        print(f"           {Colors.RED}{detail}{Colors.RESET}")


def run_all():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  端到端测试 - 个人博客系统{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    # 初始化数据库
    Base.metadata.create_all(bind=db_module.engine)
    db = SessionLocal()
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # 种子数据
    admin = User(
        username="admin", email="admin@example.com",
        hashed_password=pwd.hash("admin123"),
        nickname="管理员", is_active=True, is_admin=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    tech = Category(name="技术", slug="tech", description="技术")
    db.add(tech)
    db.commit()
    db.refresh(tech)

    py_tag = Tag(name="Python", slug="python")
    db.add(py_tag)
    db.commit()

    # 构建应用并创建客户端
    app = build_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    total = 0
    failures = 0

    def check(label, condition, detail=""):
        nonlocal total, failures
        total += 1
        if condition:
            passed(label)
        else:
            failures += 1
            failed(label, detail)

    # ===== 流程 1: 健康检查 =====
    print(f"{Colors.CYAN}[1/7] 健康检查{Colors.RESET}")
    resp = client.get("/health")
    check("状态码 200", resp.status_code == 200, f"got {resp.status_code}")
    data = resp.json()
    check("status == healthy", data.get("status") == "healthy", f"got {data.get('status')}")

    # ===== 流程 2: 登录 =====
    print(f"\n{Colors.CYAN}[2/7] 登录{Colors.RESET}")
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    check("状态码 200", resp.status_code == 200, resp.text[:200])
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data.get("access_token", "")
        check("返回 access_token", len(token) > 0)
        check("token_type == bearer", token_data.get("token_type") == "bearer")
    else:
        token = ""

    # ===== 流程 3: 创建文章 =====
    print(f"\n{Colors.CYAN}[3/7] 创建文章{Colors.RESET}")
    resp = client.post(
        "/api/posts",
        json={
            "title": "端到端测试文章",
            "content": "# 测试文章正文\n\n这是用于端到端测试的文章。",
            "summary": "E2E 测试文章",
            "is_published": True,
            "slug": "e2e-test-article",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    check("状态码 201", resp.status_code == 201, resp.text[:200])
    post_id = None
    post_slug = "e2e-test-article"
    if resp.status_code == 201:
        post_data = resp.json()
        post_id = post_data.get("id")
        check("title 正确", post_data.get("title") == "端到端测试文章")
        check("slug 正确", post_data.get("slug") == post_slug)
        check("is_published == True", post_data.get("is_published") is True)
        check("author == admin", post_data.get("author", {}).get("username") == "admin")

    # ===== 流程 4: 首页列表 =====
    print(f"\n{Colors.CYAN}[4/7] 首页文章列表{Colors.RESET}")
    resp = client.get("/api/posts?page=1&page_size=10")
    check("状态码 200", resp.status_code == 200)
    if resp.status_code == 200:
        list_data = resp.json()
        check("total >= 1", list_data.get("total", 0) >= 1, f"total={list_data.get('total')}")
        check("page == 1", list_data.get("page") == 1)
        check("total_pages >= 1", list_data.get("total_pages", 0) >= 1)
        slugs = [p["slug"] for p in list_data.get("items", [])]
        check(f"文章 '{post_slug}' 在列表中", post_slug in slugs, f"slugs={slugs}")

    # ===== 流程 5: 文章详情 =====
    print(f"\n{Colors.CYAN}[5/7] 文章详情{Colors.RESET}")
    resp = client.get(f"/api/posts/{post_slug}")
    check("状态码 200", resp.status_code == 200, resp.text[:200])
    if resp.status_code == 200:
        detail = resp.json()
        check("slug 正确", detail.get("slug") == post_slug)
        check("title 正确", detail.get("title") == "端到端测试文章")
        check("content 正确", "测试文章正文" in detail.get("content", ""))
        check("view_count >= 1", detail.get("view_count", 0) >= 1,
              f"view_count={detail.get('view_count')}")

    # ===== 流程 6: 更新文章 =====
    print(f"\n{Colors.CYAN}[6/7] 更新文章{Colors.RESET}")
    if post_id:
        resp = client.put(
            f"/api/posts/{post_id}",
            json={"title": "更新后的标题"},
            headers={"Authorization": f"Bearer {token}"},
        )
        check("状态码 200", resp.status_code == 200, resp.text[:200])
        if resp.status_code == 200:
            check("title 已更新", resp.json().get("title") == "更新后的标题")

        # 验证更新后详情
        resp = client.get(f"/api/posts/{post_slug}")
        check("详情 title 已更新", resp.json().get("title") == "更新后的标题")

    # ===== 流程 7: 删除并验证 =====
    print(f"\n{Colors.CYAN}[7/7] 删除文章并验证{Colors.RESET}")
    if post_id:
        resp = client.delete(
            f"/api/posts/{post_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        check("状态码 204", resp.status_code == 204, f"got {resp.status_code}")

        # 验证列表不再包含
        resp = client.get("/api/posts?page=1&page_size=10")
        if resp.status_code == 200:
            slugs = [p["slug"] for p in resp.json().get("items", [])]
            check("文章已从列表消失", post_slug not in slugs)

        # 验证详情 404
        resp = client.get(f"/api/posts/{post_slug}")
        check("详情返回 404", resp.status_code == 404, f"got {resp.status_code}")

    db.close()

    # ===== 汇总 =====
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"  总计: {total} 项测试 | "
          f"{Colors.GREEN}通过 {total - failures}{Colors.RESET} | "
          f"{Colors.RED}失败 {failures}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    return failures == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
