/**
 * API 客户端工具
 * 用于与后端 API 通信获取文章数据
 */

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || '/api';

/**
 * 获取所有文章列表
 */
export async function fetchPosts(): Promise<Post[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts`);
    if (!response.ok) {
      throw new Error(`Failed to fetch posts: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching posts:', error);
    // 降级方案：返回本地数据
    return [];
  }
}

/**
 * 获取单篇文章详情
 */
export async function fetchPost(slug: string): Promise<Post | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${slug}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch post: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching post ${slug}:`, error);
    return null;
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
    console.error('Error searching posts:', error);
    return [];
  }
}

/**
 * 创建新文章
 */
export async function createPost(post: CreatePostInput): Promise<Post | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(post),
    });
    if (!response.ok) {
      throw new Error(`Failed to create post: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating post:', error);
    return null;
  }
}

/**
 * 更新文章
 */
export async function updatePost(slug: string, post: Partial<CreatePostInput>): Promise<Post | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${slug}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(post),
    });
    if (!response.ok) {
      throw new Error(`Failed to update post: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error updating post ${slug}:`, error);
    return null;
  }
}

/**
 * 删除文章
 */
export async function deletePost(slug: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${slug}`, {
      method: 'DELETE',
    });
    return response.ok;
  } catch (error) {
    console.error(`Error deleting post ${slug}:`, error);
    return false;
  }
}

// 类型定义
export interface Post {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  date: string;
  tags: string[];
}

export interface CreatePostInput {
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  tags: string[];
}
