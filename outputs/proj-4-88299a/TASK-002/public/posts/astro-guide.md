# Astro 框架入门指南

探索 Astro 静态站点生成器的核心概念与最佳实践。

## 什么是 Astro？

Astro 是一个现代的静态站点生成器，专注于性能和开发者体验。它采用"岛屿架构"（Islands Architecture），让页面大部分内容都是静态 HTML，只有需要交互的部分才加载 JavaScript。

## 核心特性

### 零 JavaScript 默认

Astro 默认生成零 JavaScript 的静态 HTML 页面，只有当你需要交互时才加载 JS。

```javascript
// 零 JS 运行时
const page = await Astro.render();
// 输出纯静态 HTML
```

### 组件 Islands

使用 `client:*` 指令控制组件的水合（hydration）：

```astro
---
import Counter from './Counter.astro';
---
<!-- 只在可见时加载 -->
<Counter client:visible />
<!-- 页面加载时立即加载 -->
<Counter client:load />
<!-- 只在 idle 时加载 -->
<Counter client:idle />
```

### 多框架支持

Astro 可以使用 React、Vue、Svelte 等框架的组件：

```astro
---
import ReactCounter from './ReactCounter.jsx';
import VueCounter from './VueCounter.vue';
---
<ReactCounter client:visible />
<VueCounter client:visible />
```

## 快速开始

```bash
# 创建新项目
npm create astro@latest

# 启动开发服务器
npm run dev

# 构建静态站点
npm run build
```

## 为什么选择 Astro？

1. **极致性能** - 静态 HTML 优先，最小 JS 加载
2. **简单易用** - 类似 JSX 的语法，上手快
3. **灵活集成** - 支持多种 UI 框架
4. **SEO 友好** - 静态生成天然适合搜索引擎

## 总结

Astro 是构建内容密集型网站的理想选择，博客、文档站点、营销页面都能从中受益。