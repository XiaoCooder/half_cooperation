# TASK-004: 后端 - 认证 API 路由

## 任务概述

实现 `/api/auth/login`, `/api/auth/logout`, `/api/auth/me` 三个核心认证接口，整合 TASK-002 数据库配置和 TASK-003 认证逻辑。

## 产出文件

| 文件名 | 说明 |
|--------|------|
| `auth_api.py` | 认证 API 路由 - 核心三个接口实现 |
| `main.py` | FastAPI 主应用 - 可直接运行 |
| `test_auth_api.py` | API 接口测试 |
| `examples.py` | 请求示例集合 |

## API 端点

### 核心接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/login` | POST | ❌ | 用户登录（JSON） |
| `/api/auth/login/form` | POST | ❌ | 用户登录（OAuth2表单） |
| `/api/auth/logout` | POST | ✅ | 用户登出 |
| `/api/auth/me` | GET | ✅ | 获取当前用户信息 |
| `/api/auth/me` | PATCH | ✅ | 更新用户信息 |

### 辅助接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/refresh` | POST | ❌ | 刷新 Token |
| `/api/auth/verify` | GET | ✅ | 验证 Token |

## 使用方法

### 1. 启动服务器
```bash
cd outputs/proj-5-2b46f7/TASK-004
python main.py
```

### 2. 访问 API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 测试接口

#### 使用 curl
```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 获取用户信息
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

#### 使用 HTTPie
```bash
# 登录
http POST :8000/api/auth/login username=testuser password=password123

# 获取用户信息
http :8000/api/auth/me Authorization:"Bearer <token>"
```

### 4. 运行测试
```bash
pytest test_auth_api.py -v
```

## 请求/响应格式

### 登录请求
```json
POST /api/auth/login
{
  "username": "testuser",
  "password": "password123"
}
```

### 登录响应
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 用户信息响应
```json
GET /api/auth/me
Authorization: Bearer eyJhbG...

{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "nickname": "Test User",
  "avatar": null,
  "bio": null,
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-04-11T10:00:00Z",
  "updated_at": null
}
```

### 登出响应
```json
POST /api/auth/logout
Authorization: Bearer eyJhbG...

{
  "message": "User 'testuser' logged out successfully",
  "success": true
}
```

## 模块依赖

本任务依赖以下前序任务输出：

| 任务 | 模块 | 导入内容 |
|------|------|----------|
| TASK-002 | `database.py` | `get_db` - 数据库会话依赖 |
| TASK-002 | `models.py` | `User` - 用户模型 |
| TASK-003 | `security.py` | 密码哈希/验证函数 |
| TASK-003 | `auth.py` | JWT Token 相关函数 |
| TASK-003 | `auth_service.py` | `AuthService` - 认证服务类 |

## 安全配置

生产环境部署前，请确保：

1. **修改 SECRET_KEY**: 设置至少 32 字符的随机密钥
2. **HTTPS**: 生产环境必须使用 HTTPS
3. **Token 黑名单**: 如需服务器端登出控制，添加 Redis token 黑名单

## 注意事项

- 路径前缀使用 `/api/auth`，符合 RESTful 规范
- OAuth2 表单登录用于 Swagger UI 测试
- 登出仅返回成功消息，客户端需自行删除本地 token
- Token 在过期前仍有效（JWT 无状态特性）