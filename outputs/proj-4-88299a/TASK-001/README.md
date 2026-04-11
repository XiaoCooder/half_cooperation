# Sci-Fi Blog

科幻风格个人博客项目

## 技术栈

- [Astro](https://astro.build) - 静态站点生成器
- [Tailwind CSS](https://tailwindcss.com) - 样式框架
- [marked.js](https://marked.js.org) - Markdown 解析器
- [highlight.js](https://highlightjs.org) - 代码语法高亮

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建
npm run build
```

## 目录结构

```
.
├── astro.config.mjs      # Astro 配置
├── tailwind.config.mjs   # Tailwind 配置
├── package.json
├── src/
│   ├── components/       # 组件
│   ├── layouts/          # 布局
│   ├── pages/            # 页面
│   ├── styles/           # 样式
│   └── data/             # 数据
└── public/
    └── posts/            # Markdown 文章
```

## 许可证

MIT
