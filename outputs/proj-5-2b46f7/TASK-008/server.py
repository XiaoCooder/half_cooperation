"""
启动脚本与测试工具
任务码: TASK-008
用于启动服务和测试 API
"""

import sys
import os

# 添加前序任务路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

for task in ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-006", "TASK-007"]:
    task_path = os.path.join(BASE_DIR, task)
    if task_path not in sys.path:
        sys.path.insert(0, task_path)


def test_imports():
    """测试所有模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)

    modules = [
        ("database", "数据库配置"),
        ("models", "数据模型"),
        ("schemas", "Pydantic schemas"),
        ("security", "安全工具"),
        ("auth", "认证模块"),
        ("auth_api", "认证 API"),
        ("auth_service", "认证服务"),
        ("posts_admin", "文章管理 API"),
        ("markdown_storage", "Markdown 存储"),
    ]

    success = 0
    failed = 0

    for module, desc in modules:
        try:
            __import__(module)
            print(f"✅ {module:20} - {desc}")
            success += 1
        except ImportError as e:
            print(f"❌ {module:20} - {desc}: {e}")
            failed += 1

    print("=" * 50)
    print(f"导入测试结果: {success} 成功, {failed} 失败")
    print("=" * 50)

    return failed == 0


def test_cors_config():
    """测试 CORS 配置"""
    print("\n测试 CORS 配置...")

    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "test"}

    client = TestClient(app)

    # 测试 OPTIONS 预检请求
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        }
    )

    # 检查 CORS 头
    if "access-control-allow-origin" in response.headers:
        print(f"✅ CORS 头存在: {response.headers.get('access-control-allow-origin')}")
    else:
        print("❌ CORS 头缺失")

    return True


def start_server():
    """启动服务器"""
    print("=" * 50)
    print("启动服务器...")
    print("=" * 50)

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 不使用 reload，避免循环导入
        log_level="info"
    )


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="博客后端工具")
    parser.add_argument("command", choices=["test", "start", "imports"], help="命令")

    args = parser.parse_args()

    if args.command == "imports":
        test_imports()
    elif args.command == "test":
        test_imports()
        test_cors_config()
    elif args.command == "start":
        start_server()


if __name__ == "__main__":
    main()