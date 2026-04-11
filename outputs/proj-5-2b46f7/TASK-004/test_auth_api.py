"""
认证 API 接口测试
任务码: TASK-004
测试 /api/auth/login, /api/auth/logout, /api/auth/me 接口
"""

import pytest
import sys
import os

# 添加模块路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK002_PATH = os.path.join(BASE_DIR, "TASK-002")
TASK003_PATH = os.path.join(BASE_DIR, "TASK-003")

sys.path.insert(0, TASK002_PATH)
sys.path.insert(0, TASK003_PATH)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

# 导入主应用
from main import app


# ============== 测试客户端 ==============

client = TestClient(app)


# ============== 测试类 ==============

class TestHealthCheck:
    """健康检查测试"""

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "0.3.0"

    def test_health_endpoint(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "blog-backend"


class TestAuthLogin:
    """登录接口测试"""

    @patch('auth_api.AuthService')
    @patch('auth_api.get_db')
    def test_login_success(self, mock_get_db, mock_auth_service):
        """测试登录成功"""
        # 模拟数据库
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        # 模拟认证服务返回 token
        from datetime import datetime, timezone, timedelta
        mock_token_pair = MagicMock()
        mock_token_pair.access_token = "test_access_token"
        mock_token_pair.refresh_token = "test_refresh_token"
        mock_token_pair.access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=30)

        mock_service_instance = MagicMock()
        mock_service_instance.login.return_value = mock_token_pair
        mock_auth_service.return_value = mock_service_instance

        # 发送登录请求
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_missing_fields(self):
        """测试缺少必填字段"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}  # 缺少 password
        )
        assert response.status_code == 422  # Validation error

    def test_login_invalid_username_length(self):
        """测试用户名长度不合法"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "ab",  # 少于 3 字符
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_login_invalid_password_length(self):
        """测试密码长度不合法"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "12345"  # 少于 6 字符
            }
        )
        assert response.status_code == 422


class TestAuthLogout:
    """登出接口测试"""

    def test_logout_without_token(self):
        """测试未携带 token 登出"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    @patch('auth_api.verify_access_token')
    @patch('auth_api.AuthService')
    @patch('auth_api.get_db')
    def test_logout_with_valid_token(self, mock_get_db, mock_auth_service, mock_verify_token):
        """测试携带有效 token 登出"""
        # 模拟 token 验证
        mock_verify_token.return_value = {"sub": "1", "username": "testuser"}

        # 模拟数据库和用户
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.is_active = True

        mock_service_instance = MagicMock()
        mock_service_instance.get_current_user.return_value = mock_user
        mock_auth_service.return_value = mock_service_instance

        # 发送登出请求
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["success"] is True


class TestAuthMe:
    """获取当前用户接口测试"""

    def test_me_without_token(self):
        """测试未携带 token 获取用户信息"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    @patch('auth_api.verify_access_token')
    @patch('auth_api.AuthService')
    @patch('auth_api.get_db')
    def test_me_with_valid_token(self, mock_get_db, mock_auth_service, mock_verify_token):
        """测试携带有效 token 获取用户信息"""
        from datetime import datetime, timezone

        # 模拟 token 验证
        mock_verify_token.return_value = {"sub": "1", "username": "testuser"}

        # 模拟数据库和用户
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.nickname = "Test User"
        mock_user.avatar = None
        mock_user.bio = None
        mock_user.is_active = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.now(timezone.utc)
        mock_user.updated_at = None

        mock_service_instance = MagicMock()
        mock_service_instance.get_current_user.return_value = mock_user
        mock_auth_service.return_value = mock_service_instance

        # 发送获取用户信息请求
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data


class TestAPIPaths:
    """API 路径测试"""

    def test_auth_router_prefix(self):
        """测试认证路由前缀"""
        # 验证所有认证接口都在 /api/auth 下
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_spec = response.json()

        paths = openapi_spec.get("paths", {})
        auth_paths = [p for p in paths.keys() if "/api/auth" in p]

        assert "/api/auth/login" in auth_paths
        assert "/api/auth/logout" in auth_paths
        assert "/api/auth/me" in auth_paths


# ============== 运行测试 ==============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


"""
测试运行命令:
    python test_auth_api.py
    pytest test_auth_api.py -v

依赖安装:
    pip install pytest fastapi httpx
"""