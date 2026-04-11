# 新建/编辑文章页面

任务码: TASK-012

## 功能概述

实现管理后台的文章新建和编辑功能，支持 Markdown 编辑器。

## 页面

### 1. 新建文章 - /admin/new

访问路径：`/admin/new` 或 `/admin/new.html`

功能：
- 标题输入（必填）
- Slug 自动生成（可手动修改）
- 摘要输入
- 封面图 URL
- 分类选择
- 标签多选
- Markdown 编辑器（实时预览）
- 发布状态切换

### 2. 编辑文章 - /admin/edit?id={id}

访问路径：`/admin/edit.html?id=123`

功能：
- 自动加载文章内容
- 编辑器工具栏（粗体、斜体、标题、链接、图片、代码、列表、引用）
- 实时 Markdown 预览
- 保存更改

## 文件结构

```
TASK-012/
├── postEditorApi.ts       # 文章编辑 API 客户端
├── adminNew.astro         # 新建文章页面
├── adminEditParam.astro   # 编辑文章页面（查询参数方式）
├── adminEditDynamic.astro  # 编辑页面（动态路由预留）
└── README.md              # 本文档
```

## 使用方式

### 复制到前端项目

```bash
# 复制 API 客户端
cp postEditorApi.ts ../TASK-009/src/utils/

# 复制页面文件
cp adminNew.astro ../TASK-009/src/pages/admin/
cp adminEditParam.astro ../TASK-009/src/pages/admin/
```

### 添加 marked 依赖

需要安装 marked 库用于 Markdown 解析：

```bash
npm install marked
```

### 访问页面

- 新建：`http://localhost:5173/admin/new`
- 编辑：`http://localhost:5173/admin/edit.html?id=123`

## API 客户端

### `fetchPostForEdit(postId: number)`

获取文章详情（包含完整 content）

### `createPost(input: CreatePostInput)`

创建文章

### `updatePost(postId: number, input: UpdatePostInput)`

更新文章

### `fetchCategories()`

获取分类列表

### `fetchTags()`

获取标签列表

## 依赖

- TASK-010: 认证模块 (auth.ts)
- TASK-011: adminPostsApi.ts
- marked (Markdown 解析)

## 协作

与 TASK-011 管理后台首页配合：
- `/admin` - 文章列表
- `/admin/new` - 新建文章
- `/admin/edit.html?id=123` - 编辑文章