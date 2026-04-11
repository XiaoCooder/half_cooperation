# 个人博客系统 - 前端

基于 Astro + Tailwind CSS 构建的科幻风格博客前端，支持前后端分离架构。

## 项目特性

- 🚀 **Astro 5.0** - 极速静态站点生成
- 🎨 **Tailwind CSS** - 科幻霓虹风格设计
- 🔌 **API 代理配置** - 开发时自动代理到后端
- 📱 **响应式布局** - 完美适配各种设备
- 📝 **Markdown 渲染** - 支持代码高亮

## 技术架构

### 前后端分离

```
┌─────────────────┐         ┌─────────────────┐
│   Astro 前端    │ ◄─────► │   后端 API      │
│   (Port 3000)   │  /api   │   (Port 5000)   │
└─────────────────┘         └─────────────────┘
```

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
# API 基础 URL
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
│   │   ├── index.astro   # 首页
│   │   ├── chat.astro    # AI 对话页
│   │   └── posts/
│   │       └── [slug].astro  # 文章详情页
│   ├── styles/
│   │   └── global.css    # 全局样式
│   └── utils/
│       └── api.ts        # API 客户端工具
└── public/
    ├── favicon.svg
    └── posts/            # Markdown 文章（本地存储）
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

# 构建
npm run build

# 预览构建结果
npm run preview
```

## API 接口规范

前端期望后端提供以下 RESTful API：

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/posts` | 获取所有文章列表 |
| GET | `/api/posts/:slug` | 获取单篇文章详情 |
| GET | `/api/posts/search?q=keyword` | 搜索文章 |
| POST | `/api/posts` | 创建新文章 |
| PUT | `/api/posts/:slug` | 更新文章 |
| DELETE | `/api/posts/:slug` | 删除文章 |

### 文章数据结构

```typescript
interface Post {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  date: string;
  tags: string[];
}
```

## 降级策略

当后端 API 不可用时，前端会自动降级使用本地 `posts.ts` 中的静态数据，确保页面仍可正常渲染。
