# TASK-015: 端到端测试与验证

## 测试覆盖

完整流程: **登录 → 创建文章 → 首页显示 → 文章详情 → 更新 → 删除 → 验证消失**

### 测试文件

| 文件 | 说明 |
|------|------|
| `test_e2e.py` | pytest 格式的端到端集成测试 |
| `e2e_runner.py` | 独立运行脚本（无需 pytest） |

### 测试场景

#### 主流程 (TestEndToEnd)
1. **健康检查** - GET /health
2. **根路径** - GET /
3. **登录** - POST /api/auth/login → 获取 JWT token
4. **创建文章** - POST /api/posts → 201 Created
5. **首页列表** - GET /api/posts → 验证文章出现在列表中
6. **文章详情** - GET /api/posts/{slug} → 验证内容 + 浏览次数 +1
7. **更新 + 删除** - PUT → DELETE → 验证列表消失 + 详情 404

#### 认证边界 (TestAuthEdgeCases)
- 错误密码 → 401
- 不存在用户 → 401
- 无认证创建文章 → 401
- 无效 token → 401
- 无认证删除 → 401

#### 公开接口边界 (TestPublicPostsEdgeCases)
- 空列表
- 草稿不出现在列表
- 草稿详情 → 404
- 不存在的 slug → 404

#### 分页 (TestPagination)
- 分页参数正确性
- 多页数据分割
- 非法参数 → 422

### 运行方式

```bash
# 方式一: pytest
cd outputs/proj-5-2b46f7/TASK-015
pytest test_e2e.py -v -s

# 方式二: 独立脚本
python e2e_runner.py
```

### 依赖的前序任务

- TASK-001: FastAPI 基础
- TASK-002: 数据库模型
- TASK-003: JWT 认证基础
- TASK-004: 认证 API 路由 (auth_api)
- TASK-005: 公开文章路由
- TASK-006: 文章管理路由 (posts_admin)
