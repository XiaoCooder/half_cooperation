# TASK-005: 后端 - 文章 API 路由（公开）

## 实现内容

### 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/posts` | 获取已发布文章列表（分页） |
| GET | `/api/posts/{slug}` | 获取文章详情（按 slug） |

### 查询参数（列表接口）

- `page` (int, 默认 1): 页码
- `page_size` (int, 默认 10, 最大 100): 每页条数
- `category` (string, 可选): 按分类 slug 筛选
- `tag` (string, 可选): 按标签 slug 筛选

### 响应体

- 列表接口返回 `PaginatedResponse`：包含 `total`, `page`, `page_size`, `total_pages`, `items`
- 详情接口返回 `PostResponse`：包含文章完整信息及作者、分类、标签

### 关键设计

1. **仅返回已发布文章**：两个接口都过滤 `is_published=True`
2. **预加载关联数据**：使用 `joinedload` 避免 N+1 查询
3. **浏览次数统计**：详情接口每次访问将 `view_count` +1
4. **分页响应**：遵循 TASK-002 定义的 `PaginatedResponse` schema

### 依赖的前序任务

- TASK-001: FastAPI 项目基础、`database.py`、`config.py`
- TASK-002: 数据模型（`models.py`）、Pydantic schemas（`schemas.py`）、数据库工具（`db_utils.py`）

### 集成方式

在 `main.py` 中导入并注册路由：

```python
from posts import router as posts_router
app.include_router(posts_router)
```

### 测试

```bash
cd /path/to/backend
pytest test_posts_api.py -v
```
