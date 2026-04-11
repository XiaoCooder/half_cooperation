# 个人博客系统 - 前端

基于 Astro + Tailwind CSS 构建的科幻风格博客前端，支持前后端分离架构。

## 项目特性

- 🚀 **Astro 5.0** - 极速静态站点生成
- 🎨 **Tailwind CSS** - 科幻霓虹风格设计
- 🔌 **API 集成** - 首页和文章页从后端 API 获取数据
- 📱 **响应式布局** - 完美适配各种设备
- 📝 **Markdown 渲染** - 支持代码高亮
- ⚡ **降级策略** - API 不可用时自动使用本地数据

## 技术架构

### 前后端分离

```
┌─────────────────┐         ┌─────────────────┐
│   Astro 前端    │ ◄─────► │   后端 API      │
│   (Port 3000)   │  /api   │   (Port 5000)   │
└─────────────────┘         └─────────────────┘
```

### API 集成

#### 首页 (`src/pages/index.astro`)
在服务器端通过 `fetchPostsFromAPI()` 从后端获取文章列表：
- 开发模式：`/api/posts` → 代理到后端
- 生产模式：`${API_BASE_URL}/posts`
- 超时控制：5 秒
- 失败降级：使用本地 `posts.ts` 数据

#### 文章详情页 (`src/pages/posts/[slug].astro`)
在服务器端通过 `fetchPostFromAPI(slug)` 从后端获取单篇文章：
- 开发模式：`/api/posts/{slug}` → 代理到后端
- 生产模式：`${API_BASE_URL}/posts/{slug}`
- 返回完整文章内容（含 Markdown）
- 显示浏览次数（`view_count`）

### API 配置

开发模式下，前端通过 Vite 代理将 `/api/*` 请求转发到后端服务器（默认 `http://localhost:5000`）。

编辑 `astro.config.mjs` 修改代理目标：

```javascript
vite: {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
}
```

### 环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# API 基础 URL（开发时使用代理，生产时使用实际域名）
PUBLIC_API_BASE_URL=/api
```

## 目录结构

```
├── astro.config.mjs      # Astro 配置（含 API 代理）
├── package.json
├── tailwind.config.mjs
├── tsconfig.json
├── .env.example          # 环境变量模板
├── src/
│   ├── data/
│   │   └── posts.ts      # 文章数据（支持 API/本地降级）
│   ├── layouts/
│   │   └── Layout.astro  # 基础布局
│   ├── pages/
│   │   ├── index.astro   # 首页（API 获取文章列表）
│   │   ├── chat.astro    # AI 对话页
│   │   └── posts/
│   │       └── [slug].astro  # 文章详情页（API 获取文章内容）
│   ├── styles/
│   │   └── global.css    # 全局样式
│   └── utils/
│       └── api.ts        # API 客户端工具
└── public/
    ├── favicon.svg
    └── posts/            # Markdown 文章（本地存储，作为降级）
        ├── welcome.md
        ├── astro-guide.md
        └── ...
```

## 快速开始

```bash
# 安装依赖
npm install

# 开发模式（自动代理 API 请求）
npm run dev

# 构建（构建时会从 API 获取数据生成静态页面）
npm run build

# 预览构建结果
npm run preview
```

## API 接口规范

前端从后端 API 获取数据：

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/posts` | 获取文章列表（支持分页、筛选） |
| GET | `/api/posts/:slug` | 获取单篇文章详情（含浏览次数） |

### 文章列表响应

```typescript
{
  items: Post[],      // 文章列表
  total: number,      // 总数
  page: number,       // 当前页
  page_size: number   // 每页数量
}
```

### 文章详情响应

```typescript
interface Post {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  content: string;      // Markdown 格式正文
  date: string;
  tags: string[];
  view_count: number;   // 浏览次数
  author?: {
    id: string;
    username: string;
  };
  category?: {
    id: string;
    name: string;
  };
}
```

## 降级策略

当后端 API 不可用时，页面会自动降级使用本地 `posts.ts` 中的静态数据：

1. **首页降级**：API 获取失败时显示本地文章列表
2. **文章页降级**：API 获取失败时尝试匹配本地文章
3. **超时控制**：API 请求 5 秒超时，避免长时间等待

## 构建说明

构建时（`npm run build`），Astro 会执行以下操作：

1. 调用 `fetchPostsFromAPI()` 获取所有文章列表
2. 为每篇文章调用 `fetchPostFromAPI(slug)` 获取详情
3. 生成静态 HTML 页面（包含 API 返回的数据）
4. 输出到 `dist/` 目录

这种架构既保证了静态站点的性能优势，又支持从后端 API 动态获取数据。
