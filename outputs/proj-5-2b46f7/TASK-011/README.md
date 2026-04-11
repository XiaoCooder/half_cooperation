# TASK-011: 前端 - 管理后台首页

## 实现内容

### 页面 (`admin.astro`)

**路径**: `/admin`

- 文章列表表格（标题、状态、分类、浏览量、创建时间、操作）
- 统计卡片（总文章数、已发布数、草稿数）
- 分页控件（上一页/下一页 + 页码信息）
- 新建文章按钮（跳转 `/admin/posts/new`）
- 行内操作：编辑（跳转 `/admin/posts/edit/{id}`）、删除（确认弹窗 + API 调用）

### 认证守卫

- 页面加载时检查 `authStore.getState().isAuthenticated`
- 未登录自动跳转 `/login?redirect=/admin`
- 已登录显示用户名和登出按钮

### API 客户端 (`adminPostsApi.ts`)

| 函数 | 说明 |
|------|------|
| `fetchAdminPosts(page, pageSize)` | 获取文章列表（分页） |
| `createAdminPost(input)` | 创建文章 |
| `updateAdminPost(postId, input)` | 更新文章（通过 ID） |
| `deleteAdminPost(postId)` | 删除文章（通过 ID） |
| `requireAdminAuth()` | 认证守卫检查 |

### 依赖的前序任务

- TASK-005: 公开文章列表 API (`GET /api/posts`)
- TASK-006: 管理文章 API (`POST/PUT/DELETE /api/posts/{id}`)，JWT 认证
- TASK-009: Astro + Tailwind 前端基础、Layout 布局、全局样式
- TASK-010: `auth.ts`（`authFetch`、`isAuthenticated`）、`authStore.ts`（状态管理）

### 集成方式

将 `admin.astro` 复制到前端项目的 `src/pages/` 目录：

```bash
cp admin.astro ../TASK-009/src/pages/admin.astro
cp adminPostsApi.ts ../TASK-009/src/utils/
```

确保前端项目已安装 TASK-010 的 `auth.ts` 和 `authStore.ts` 到 `src/utils/`。

### 测试

```bash
cd ../TASK-009
npx vitest run test_adminPostsApi.ts
```
