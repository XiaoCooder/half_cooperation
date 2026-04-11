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
    excerpt: '这是我的第一篇博客文章，带你探索科幻世界的边界。'
  }
];
---
