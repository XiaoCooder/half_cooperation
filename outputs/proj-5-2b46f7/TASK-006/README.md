# TASK-006: 后端 - 文章 API 路由（管理）

## 实现内容

### 认证模块 (`auth.py`)

| 函数 | 说明 |
|------|------|
| `create_access_token(data, expires_delta)` | 生成 JWT access token |
| `decode_access_token(token)` | 解码并验证 JWT |
| `get_current_user(token, db)` | FastAPI 依赖：从 Bearer token 提取当前用户 |
| `get_current_admin_user(current_user)` | FastAPI 依赖：验证管理员权限 |
| `get_password_hash(password)` | bcrypt 密码哈希 |
| `verify_password(plain, hashed)` | 密码验证 |

### 管理接口 (`posts_admin.py`)

| 方法 | 路径 | 权限 | 描述 |
|------|------|------|------|
| POST | `/api/posts` | 已登录用户 | 创建文章 |
| PUT | `/api/posts/{id}` | 作者或管理员 | 更新文章 |
| DELETE | `/api/posts/{id}` | 作者或管理员 | 删除文章 |

### 查询参数与响应

- **创建文章**：接收 `PostCreate`（title, content, slug, summary, cover_image, is_published, category_id, tag_ids），返回 `PostResponse`，状态码 201
- **更新文章**：接收 `PostUpdate`（部分字段），返回 `PostResponse`
- **删除文章**：无请求体，状态码 204

### 权限模型

- 创建：任何已登录用户
- 更新/删除：文章作者 或 管理员（`is_admin=True`）
- 未认证返回 401，无权返回 403

### Slug 生成

创建文章时若未提供 `slug`，自动从 `title` 生成（小写、字母数字+连字符），并保证唯一性（冲突时追加数字后缀）。

### 依赖的前序任务

- TASK-001: FastAPI 项目基础、`config.py`（SECRET_KEY）、`requirements.txt`
- TASK-002: 数据模型、Pydantic schemas、数据库工具
- TASK-005: 公开文章路由（共享同一 `/api/posts` 前缀）

### 集成方式

```python
from posts_admin import router as posts_admin_router
app.include_router(posts_admin_router)
```

### 测试

```bash
cd /path/to/backend
pytest test_posts_admin.py -v
```
