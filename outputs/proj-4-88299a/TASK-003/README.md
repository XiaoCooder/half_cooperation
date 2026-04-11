# Sci-Fi Blog

科幻风格个人博客项目

## 技术栈

- [Astro](https://astro.build) - 静态站点生成器
- [Tailwind CSS](https://tailwindcss.com) - 样式框架
- [marked.js](https://marked.js.org) - Markdown 解析器
- [highlight.js](https://highlightjs.org) - 代码语法高亮

## 样式系统

### 科幻风格配色

| 颜色 | 用途 | 值 |
|------|------|-----|
| `scifi-bg` | 深空黑背景 | `#0a0a0f` |
| `scifi-primary` | 青色霓虹 | `#00d4ff` |
| `scifi-secondary` | 紫色霓虹 | `#7000ff` |
| `scifi-accent` | 粉色霓虹 | `#ff006e` |

### 核心视觉效果

1. **网格背景动画** - 50px 网格线持续移动
2. **霓虹光效** - 文字、边框、按钮发光效果
3. **Hero 背景光效** - 多色渐变径向光效动画
4. **卡片悬浮效果** - 渐变边框 + 悬浮动画
5. **脉冲发光** - 按钮和 Logo 呼吸动画

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
├── tailwind.config.mjs   # Tailwind 配置（含科幻配色+动画）
├── package.json
├── src/
│   ├── layouts/          # 布局组件（含导航+页脚）
│   ├── pages/            # 页面
│   │   ├── index.astro   # 首页（Hero+文章列表+CTA）
│   │   ├── chat.astro    # AI对话页
│   │   └── posts/        # 文章详情页
│   ├── styles/           # 样式
│   │   └ global.css      # 全局科幻样式系统
│   └── data/             # 数据
│       └ posts.ts        # 文章元数据
└── public/
    ├── favicon.svg       # 网站图标
    └── posts/            # Markdown 文章
```

## 首页布局

### Hero 区域
- 背景光效动画（青/紫/粉三色渐变）
- 主标题渐变文字效果
- 状态指示器（脉冲动画）
- CTA 按钮（霓虹按钮样式）

### 文章卡片列表
- 双列网格布局
- 卡片悬浮效果（渐变边框）
- 序号标识 + 标签显示
- 装饰性底部渐变线

### 页脚
- 三列布局：Logo + 链接 + 技术栈
- 社交链接图标
- 状态指示器
- 底部装饰渐变线

## 许可证

MIT