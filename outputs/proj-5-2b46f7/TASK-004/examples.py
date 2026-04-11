"""
请求示例集合
任务码: TASK-004
提供各接口的请求示例，便于测试和文档
"""

import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

# ============== 示例请求 ==============


def example_login_json():
    """
    登录接口示例（JSON 格式）

    POST /api/auth/login
    """
    url = f"{BASE_URL}/api/auth/login"

    payload = {
        "username": "testuser",
        "password": "password123"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("=" * 50)
    print("POST /api/auth/login")
    print("=" * 50)
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_login_form():
    """
    登录接口示例（OAuth2 表单格式）

    POST /api/auth/login/form
    """
    url = f"{BASE_URL}/api/auth/login/form"

    data = {
        "username": "testuser",
        "password": "password123"
    }

    response = requests.post(url, data=data)

    print("=" * 50)
    print("POST /api/auth/login/form")
    print("=" * 50)
    print(f"Request (form-data): username=testuser, password=password123")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_logout(access_token: str):
    """
    登出接口示例

    POST /api/auth/logout
    """
    url = f"{BASE_URL}/api/auth/logout"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, headers=headers)

    print("=" * 50)
    print("POST /api/auth/logout")
    print("=" * 50)
    print(f"Headers: Authorization: Bearer {access_token[:20]}...")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_get_me(access_token: str):
    """
    获取当前用户信息示例

    GET /api/auth/me
    """
    url = f"{BASE_URL}/api/auth/me"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    print("=" * 50)
    print("GET /api/auth/me")
    print("=" * 50)
    print(f"Headers: Authorization: Bearer {access_token[:20]}...")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_update_me(access_token: str):
    """
    更新用户信息示例

    PATCH /api/auth/me
    """
    url = f"{BASE_URL}/api/auth/me"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "nickname": "新昵称",
        "bio": "这是我的个人简介"
    }

    response = requests.patch(url, json=payload, headers=headers)

    print("=" * 50)
    print("PATCH /api/auth/me")
    print("=" * 50)
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_refresh_token(refresh_token: str):
    """
    刷新 Token 示例

    POST /api/auth/refresh
    """
    url = f"{BASE_URL}/api/auth/refresh"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "refresh_token": refresh_token
    }

    response = requests.post(url, json=payload, headers=headers)

    print("=" * 50)
    print("POST /api/auth/refresh")
    print("=" * 50)
    print(f"Request: {json.dumps(payload, indent=2)[:50]}...")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


def example_verify_token(access_token: str):
    """
    验证 Token 示例

    GET /api/auth/verify
    """
    url = f"{BASE_URL}/api/auth/verify"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    print("=" * 50)
    print("GET /api/auth/verify")
    print("=" * 50)
    print(f"Headers: Authorization: Bearer {access_token[:20]}...")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 50)

    return response.json()


# ============== 完整流程示例 ==============

def full_auth_flow():
    """
    完整认证流程示例
    """
    print("\n" + "=" * 60)
    print("完整认证流程示例")
    print("=" * 60 + "\n")

    # 1. 登录
    print("\n【步骤 1】登录...")
    login_response = example_login_json()
    access_token = login_response.get("access_token")
    refresh_token = login_response.get("refresh_token")

    if not access_token:
        print("❌ 登录失败，请检查用户名和密码")
        return

    # 2. 获取用户信息
    print("\n【步骤 2】获取当前用户信息...")
    example_get_me(access_token)

    # 3. 验证 Token
    print("\n【步骤 3】验证 Token...")
    example_verify_token(access_token)

    # 4. 更新用户信息
    print("\n【步骤 4】更新用户信息...")
    example_update_me(access_token)

    # 5. 刷新 Token
    print("\n【步骤 5】刷新 Token...")
    refresh_response = example_refresh_token(refresh_token)
    new_access_token = refresh_response.get("access_token")

    # 6. 使用新 Token 获取用户信息
    print("\n【步骤 6】使用新 Token 获取用户信息...")
    if new_access_token:
        example_get_me(new_access_token)

    # 7. 登出
    print("\n【步骤 7】登出...")
    example_logout(access_token)

    print("\n" + "=" * 60)
    print("认证流程完成")
    print("=" * 60 + "\n")


# ============== HTTPie/curl 命令示例 ==============

HTTPIE_COMMANDS = """
# HTTPie 命令示例

# 登录（JSON）
http POST :8000/api/auth/login username=testuser password=password123

# 登录（表单）
http --form POST :8000/api/auth/login/form username=testuser password=password123

# 获取用户信息
http :8000/api/auth/me Authorization:"Bearer <token>"

# 登出
http POST :8000/api/auth/logout Authorization:"Bearer <token>"

# 验证 Token
http :8000/api/auth/verify Authorization:"Bearer <token>"

# 刷新 Token
http POST :8000/api/auth/refresh refresh_token="<refresh_token>"
"""

CURL_COMMANDS = """
# curl 命令示例

# 登录（JSON）
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 登录（表单）
curl -X POST http://localhost:8000/api/auth/login/form \
  -d "username=testuser&password=password123"

# 获取用户信息
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"

# 登出
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer <token>"

# 验证 Token
curl -X GET http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer <token>"

# 刷新 Token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
"""


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("认证 API 请求示例")
    print("=" * 60)

    print("\n【HTTPie 命令】")
    print(HTTPIE_COMMANDS)

    print("\n【curl 命令】")
    print(CURL_COMMANDS)

    print("\n【提示】")
    print("- 启动服务器: python main.py")
    print("- 访问文档: http://localhost:8000/docs")
    print("- 运行完整流程（需要服务器运行）: full_auth_flow()")

    # 如果服务器运行中，执行完整流程
    try:
        # 检查服务器是否运行
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("\n检测到服务器运行中，执行完整认证流程...")
            full_auth_flow()
    except:
        print("\n服务器未运行，跳过实际请求示例")
        print("请先启动服务器: python main.py")