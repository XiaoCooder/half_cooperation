/**
 * 文章数据管理
 * 支持从后端 API 或本地 Markdown 文件获取数据
 */

export interface Post {
  id?: string;
  slug: string;
  title: string;
  date: string;
  tags: string[];
  excerpt?: string;
  content?: string;
}

// API 基础 URL
const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || '/api';

/**
 * 从 API 获取所有文章列表
 */
export async function fetchPostsFromAPI(): Promise<Post[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts`);
    if (!response.ok) {
      throw new Error(`Failed to fetch posts: ${response.status}`);
    }
    const data = await response.json();
    return data.sort((a: Post, b: Post) => b.date.localeCompare(a.date));
  } catch (error) {
    console.warn('API unavailable, falling back to local data:', error);
    return posts;
  }
}

/**
 * 从 API 获取单篇文章详情
 */
export async function fetchPostFromAPI(slug: string): Promise<Post | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${slug}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch post: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn(`API unavailable, falling back to local data for ${slug}:`, error);
    const localPost = getPostBySlug(slug);
    return localPost || null;
  }
}

/**
 * 搜索文章
 */
export async function searchPosts(query: string): Promise<Post[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`Failed to search posts: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn('Search API unavailable, using local search:', error);
    // 本地搜索降级
    const lowerQuery = query.toLowerCase();
    return posts.filter(post =>
      post.title.toLowerCase().includes(lowerQuery) ||
      post.excerpt?.toLowerCase().includes(lowerQuery) ||
      post.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }
}

// 本地文章数据（作为 API 降级方案）
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
  },
  {
    slug: 'typescript-best-practices',
    title: 'TypeScript 最佳实践指南',
    date: '2025-04-12',
    tags: ['typescript', 'coding', 'tutorial'],
    excerpt: '深入探讨 TypeScript 的高级类型系统与最佳实践，提升代码质量。'
  },
  {
    slug: 'responsive-design',
    title: 'CSS 响应式设计实战',
    date: '2025-04-13',
    tags: ['css', 'design', 'responsive'],
    excerpt: '探索现代 CSS 布局技术，构建适配各种设备的界面。'
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
