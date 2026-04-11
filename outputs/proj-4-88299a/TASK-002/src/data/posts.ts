---
// 文章元数据接口
export interface Post {
  slug: string;
  title: string;
  date: string;
  tags: string[];
  excerpt?: string;
}

// 模拟文章列表数据
export const posts: Post[] = [
  {
    slug: 'welcome',
    title: '欢迎来到科幻博客',
    date: '2025-04-11',
    tags: ['intro', 'scifi'],
    excerpt: '这是我的第一篇博客文章，带你探索科幻世界的边界。在这里，代码与想象交织，技术与创新碰撞。'
  },
  {
    slug: 'astro-guide',
    title: 'Astro 框架入门指南',
    date: '2025-04-08',
    tags: ['astro', 'web', 'tutorial'],
    excerpt: '探索 Astro 静态站点生成器的核心概念与最佳实践。从零开始构建高性能的现代网站。'
  },
  {
    slug: 'neon-design',
    title: '霓虹光效设计美学',
    date: '2025-04-05',
    tags: ['design', 'css', 'scifi'],
    excerpt: '深入探讨科幻风格的视觉设计：霓虹光效、网格背景、赛博朋克配色方案的实现技巧。'
  },
  {
    slug: 'ai-chat-impl',
    title: 'AI 对话功能实现解析',
    date: '2025-04-01',
    tags: ['ai', 'claude', 'frontend'],
    excerpt: '详解如何集成 Claude AI 助手到博客系统，实现智能问答与创意探索功能。'
  }
];
---