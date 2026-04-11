# TASK-003: 后端 - 用户认证逻辑

## 任务概述

实现用户注册、密码哈希、Session 管理等认证逻辑。

## 产出文件

| 文件名 | 说明 |
|--------|------|
| `security.py` | 密码安全工具 - bcrypt 哈希与验证 |
| `auth.py` | JWT Token 模块 - 创建、验证、刷新 |
| `auth_service.py` | 认证服务层 - 业务逻辑封装 |
| `auth_router.py` | 认证路由 - RESTful API 端点 |
| `auth_schemas.py` | 认证 Pydantic 模型 - 请求/响应模式 |
| `dependencies.py` | FastAPI 依赖 - 获取当前用户 |
| `main_with_auth.py` | 应用集成示例 |
| `test_auth.py` | 单元测试 |

## 技术选型

### 密码安全
- **passlib + bcrypt**: 工作因子 12，安全哈希
- 自动 salt 处理，防止彩虹表攻击

### Token 认证
- **JWT (PyJWT)**: 无状态认证，支持分布式部署
- **OAuth2 密码模式**: 标准 FastAPI 认证流程
- Access Token: 30 分钟有效期
- Refresh Token: 7 天有效期

## API 端点

### 公开接口
| 端点 | 方法 | 说明 |
|------|------|------|
| `/auth/register` | POST | 用户注册 |
| `/auth/login` | POST | 登录（JSON） |
| `/auth/login/form` | POST | 登录（OAuth2 表单） |
| `/auth/refresh` | POST | 刷新 Token |

### 认证接口
| 端点 | 方法 | 说明 |
|------|------|------|
| `/auth/me` | GET | 获取当前用户 |
| `/auth/me` | PATCH | 更新用户信息 |
| `/auth/me/password` | POST | 修改密码 |
| `/auth/logout` | POST | 登出 |
| `/auth/verify-token` | POST | 验证 Token |

### 管理员接口
| 端点 | 方法 | 说明 |
|------|------|------|
| `/auth/admin/users` | GET | 用户列表 |
| `/auth/admin/users/{id}/deactivate` | PATCH | 禁用用户 |
| `/auth/admin/users/{id}/activate` | PATCH | 启用用户 |

## 使用方法

### 1. 安装依赖
```bash
pip install passlib bcrypt python-jose[cryptography] pydantic[email]
```

### 2. 集成到主应用
```python
from auth_router import router as auth_router

app.include_router(auth_router)
```

### 3. 使用认证依赖
```python
from dependencies import get_current_user, get_current_admin_user
from models import User

@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username}
```

### 4. 运行测试
```bash
python test_auth.py
pytest test_auth.py -v
```

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| SECRET_KEY | (见 auth.py) | JWT 签名密钥，生产环境需修改 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Access token 有效期 |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | Refresh token 有效期 |
| bcrypt__rounds | 12 | bcrypt 工作因子 |

## 安全特性

1. **密码哈希**: bcrypt 带自动 salt
2. **Token 类型检查**: access/refresh 类型验证
3. **用户状态检查**: 禁用用户无法登录
4. **管理员权限**: 分离普通用户和管理员接口
5. **自动哈希升级**: 算法升级时自动重新哈希

## 注意事项

- 生产环境必须修改 SECRET_KEY（至少 32 字符）
- 建议从环境变量读取密钥
- 如需服务器端登出控制，需额外实现 token 黑名单（Redis）
- 密码重置功能需要邮件验证，本版本暂未实现

## 后续依赖

后续任务应从本目录的 `result.json` 读取认证模块信息。