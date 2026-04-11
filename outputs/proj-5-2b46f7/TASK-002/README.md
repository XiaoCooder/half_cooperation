# Database Module - TASK-002

个人博客系统数据库模块，包含完整的模型定义和初始化工具。

## 文件说明

| 文件 | 说明 |
|------|------|
| `database.py` | 数据库配置和连接管理 |
| `models.py` | SQLAlchemy 数据模型定义 |
| `schemas.py` | Pydantic 数据验证模式 |
| `init_database.py` | 数据库初始化脚本 |
| `seed_data.py` | 种子数据填充脚本 |
| `db_utils.py` | 数据库工具函数 |

## 数据模型

### User（用户）
- `id`: 主键
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一）
- `hashed_password`: 密码哈希
- `nickname`: 昵称
- `avatar`: 头像 URL
- `bio`: 个人简介
- `is_active`: 是否激活
- `is_admin`: 是否管理员

### Post（文章）
- `id`: 主键
- `title`: 标题
- `slug`: URL 标识（唯一）
- `content`: 内容（Markdown）
- `summary`: 摘要
- `cover_image`: 封面图
- `is_published`: 是否发布
- `view_count`: 浏览次数
- `author_id`: 作者 ID（外键）
- `category_id`: 分类 ID（外键）

### Category（分类）
- `id`: 主键
- `name`: 分类名称
- `slug`: URL 标识
- `description`: 描述

### Tag（标签）
- `id`: 主键
- `name`: 标签名称
- `slug`: URL 标识

## 使用方法

### 初始化数据库

```bash
# 创建所有表
python init_database.py

# 检查数据库连接
python init_database.py --check

# 删除并重新创建（危险！）
python init_database.py --drop
```

### 填充测试数据

```bash
python seed_data.py
```

### 在 FastAPI 中使用

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Post

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()
```

## 数据库关系

```
User 1:N Post（一个用户多篇文章）
Category 1:N Post（一个分类多篇文章）
Post N:M Tag（多对多标签关系）
```
