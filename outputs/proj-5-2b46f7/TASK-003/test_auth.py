#!/usr/bin/env python3
"""
认证模块单元测试
任务码: TASK-003
测试密码哈希、JWT token、认证服务等功能
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security import hash_password, verify_password, needs_rehash
from auth import (
    create_access_token, create_refresh_token,
    verify_access_token, verify_refresh_token,
    create_token_pair, TokenPair, decode_token
)


class TestPasswordSecurity:
    """密码安全测试"""

    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # bcrypt 哈希长度

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_wrong(self):
        """测试错误密码验证"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """测试相同密码产生不同哈希（bcrypt salt）"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """JWT Token 测试"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "1", "username": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        data = {"sub": "1"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token(self):
        """测试解码访问令牌"""
        data = {"sub": "1", "username": "testuser"}
        token = create_access_token(data)

        payload = decode_token(token, expected_type="access")

        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"

    def test_decode_refresh_token(self):
        """测试解码刷新令牌"""
        data = {"sub": "1"}
        token = create_refresh_token(data)

        payload = decode_token(token, expected_type="refresh")

        assert payload["sub"] == "1"
        assert payload["type"] == "refresh"

    def test_token_expiration(self):
        """测试 token 包含过期时间"""
        data = {"sub": "1"}
        token = create_access_token(data)
        payload = decode_token(token)

        assert "exp" in payload
        assert "iat" in payload

    def test_custom_expiration(self):
        """测试自定义过期时间"""
        data = {"sub": "1"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        payload = decode_token(token)

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires_delta

        # 允许 10 秒误差
        diff = abs((exp_time - expected_exp).total_seconds())
        assert diff < 10

    def test_invalid_token_raises_error(self):
        """测试无效 token 抛出错误"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            decode_token("invalid_token_string")

    def test_wrong_token_type_raises_error(self):
        """测试错误 token 类型抛出错误"""
        from fastapi import HTTPException

        data = {"sub": "1"}
        access_token = create_access_token(data)

        with pytest.raises(HTTPException):
            decode_token(access_token, expected_type="refresh")


class TestTokenPair:
    """TokenPair 类测试"""

    def test_create_token_pair(self):
        """测试创建 token 对"""
        pair = create_token_pair(user_id=1, username="testuser")

        assert pair.access_token is not None
        assert pair.refresh_token is not None
        assert isinstance(pair, TokenPair)

    def test_token_pair_to_dict(self):
        """测试 token 对转字典"""
        pair = create_token_pair(user_id=1, username="testuser")
        result = pair.to_dict()

        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "access_token_expires_in" in result
        assert "refresh_token_expires_in" in result


class TestAuthService:
    """认证服务测试"""

    @patch('auth_service.Session')
    def test_auth_service_init(self):
        """测试认证服务初始化"""
        mock_db = Mock()
        service = AuthService(mock_db)

        assert service.db == mock_db
        assert service.secret_key is not None

    @patch('auth_service.Session')
    def test_authenticate_user_success(self):
        """测试用户认证成功"""
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.hashed_password = hash_password("password123")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        service = AuthService(mock_db)
        result = service.authenticate_user("testuser", "password123")

        assert result is not None
        assert result.username == "testuser"

    @patch('auth_service.Session')
    def test_authenticate_user_wrong_password(self):
        """测试用户认证失败（密码错误）"""
        mock_db = Mock()
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.hashed_password = hash_password("password123")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        service = AuthService(mock_db)
        result = service.authenticate_user("testuser", "wrongpassword")

        assert result is None

    @patch('auth_service.Session')
    def test_authenticate_user_not_found(self):
        """测试用户认证失败（用户不存在）"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = AuthService(mock_db)
        result = service.authenticate_user("nonexistent", "password123")

        assert result is None


# ============== 运行测试 ==============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


"""
测试运行命令:
    python test_auth.py
    pytest test_auth.py -v
    pytest test_auth.py --cov=security --cov=auth --cov=auth_service

依赖安装:
    pip install pytest pytest-cov
"""