/**
 * 文章编辑 API 客户端
 * 任务码: TASK-012
 * 用于新建/编辑文章页面
 */

import { authFetch, getAccessToken, isAuthenticated } from './auth';

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || '/api';

// ============== 类型定义 ==============

export interface PostDetail {
  id: number;
  slug: string;
  title: string;
  content: string;
  summary: string | null;
  cover_image: string | null;
  is_published: boolean;
  view_count: number;
  author: {
    id: number;
    username: string;
    nickname: string | null;
    is_active: boolean;
    created_at: string;
  };
  category: {
    id: number;
    name: string;
    slug: string;
    description: string | null;
    created_at: string;
  } | null;
  tags: {
    id: number;
    name: string;
    slug: string;
    created_at: string;
  }[];
  created_at: string;
  updated_at: string | null;
  published_at: string | null;
}

export interface CreatePostInput {
  title: string;
  content: string;
  summary?: string;
  cover_image?: string;
  slug?: string;
  is_published?: boolean;
  category_id?: number | null;
  tag_ids?: number[];
}

export interface UpdatePostInput {
  title?: string;
  content?: string;
  summary?: string;
  cover_image?: string;
  slug?: string;
  is_published?: boolean;
  category_id?: number | null;
  tag_ids?: number[] | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  created_at: string;
}

// ============== 文章 CRUD ==============

/**
 * 获取文章详情（包含完整 content）
 */
export async function fetchPostForEdit(postId: number): Promise<PostDetail> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`获取文章失败: ${response.status}`);
  }

  return await response.json();
}

/**
 * 创建文章
 */
export async function createPost(input: CreatePostInput): Promise<PostDetail> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建文章失败' }));
    throw new Error(error.detail || `创建文章失败: ${response.status}`);
  }

  return await response.json();
}

/**
 * 更新文章
 */
export async function updatePost(
  postId: number,
  input: UpdatePostInput
): Promise<PostDetail> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新文章失败' }));
    throw new Error(error.detail || `更新文章失败: ${response.status}`);
  }

  return await response.json();
}

// ============== 分类和标签 ==============

/**
 * 获取分类列表
 */
export async function fetchCategories(): Promise<Category[]> {
  const response = await fetch(`${API_BASE_URL}/categories`);
  if (!response.ok) {
    throw new Error('获取分类列表失败');
  }
  return await response.json();
}

/**
 * 获取标签列表
 */
export async function fetchTags(): Promise<Tag[]> {
  const response = await fetch(`${API_BASE_URL}/tags`);
  if (!response.ok) {
    throw new Error('获取标签列表失败');
  }
  return await response.json();
}

// ============== 认证守卫 ==============

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return isAuthenticated();
}

/**
 * 重定向到登录页
 */
export function redirectToLogin(): void {
  window.location.href = '/login';
}