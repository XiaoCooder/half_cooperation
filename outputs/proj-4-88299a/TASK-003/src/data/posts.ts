/**
 * 文章数据管理
 * 从 Markdown 文件的 YAML frontmatter 中提取元数据
 */

export interface Post {
  slug: string;
  title: string;
  date: string;
  tags: string[];
  excerpt?: string;
}

// 文章元数据列表（按日期倒序）
export const posts: Post[] = [
  {
    slug: 'welcome',
    title: '欢迎来到科幻博客',
    date: '2025-04-11',
    tags: ['intro', 'scifi'],
    excerpt: '这是我的第一篇博客文章，带你探索科幻世界的边界。'
  },
  {
    slug: 'astro-guide',
    title: 'Astro 框架入门指南',
    date: '2025-04-08',
    tags: ['astro', 'web', 'tutorial'],
    excerpt: '探索 Astro 静态站点生成器的核心概念与最佳实践。'
  },
  {
    slug: 'neon-design',
    title: '霓虹光效设计美学',
    date: '2025-04-05',
    tags: ['design', 'css', 'scifi'],
    excerpt: '深入探讨科幻风格的视觉设计：霓虹光效、网格背景、赛博朋克配色方案。'
  },
  {
    slug: 'ai-chat-impl',
    title: 'AI 对话功能实现解析',
    date: '2025-04-01',
    tags: ['ai', 'claude', 'frontend'],
    excerpt: '详解如何集成 Claude AI 助手到博客系统，实现智能问答与创意探索功能。'
  }
].sort((a, b) => b.date.localeCompare(a.date));

/**
 * 根据 slug 获取文章
 */
export function getPostBySlug(slug: string): Post | undefined {
  return posts.find(post => post.slug === slug);
}

/**
 * 获取上一篇文章
 */
export function getPrevPost(currentSlug: string): Post | undefined {
  const currentIndex = posts.findIndex(p => p.slug === currentSlug);
  if (currentIndex < posts.length - 1) {
    return posts[currentIndex + 1];
  }
  return undefined;
}

/**
 * 获取下一篇文章
 */
export function getNextPost(currentSlug: string): Post | undefined {
  const currentIndex = posts.findIndex(p => p.slug === currentSlug);
  if (currentIndex > 0) {
    return posts[currentIndex - 1];
  }
  return undefined;
}

/**
 * 获取所有文章的 slug 列表（用于 getStaticPaths）
 */
export function getAllPostSlugs(): string[] {
  return posts.map(post => post.slug);
}
