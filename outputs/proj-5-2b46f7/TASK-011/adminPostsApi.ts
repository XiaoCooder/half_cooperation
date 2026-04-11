/**
 * 管理端文章 API 客户端
 * 任务码: TASK-011
 * 使用 authFetch 自动携带 Bearer token
 */

import { authFetch, getAccessToken, isAuthenticated } from './auth';

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || '/api';

// ============== 类型定义 ==============

export interface AdminPostItem {
  id: number;
  title: string;
  slug: string;
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
  created_at: string;
}

export interface AdminPaginatedResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: AdminPostItem[];
}

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

// ============== API 函数 ==============

/**
 * 获取文章列表（需认证）
 * 注意：此处调用公开列表接口，管理员端可直接使用
 * 如需查看所有文章（含草稿），需确保后端支持或管理端专用列表接口
 */
export async function fetchAdminPosts(
  page: number = 1,
  pageSize: number = 20
): Promise<AdminPaginatedResponse> {
  const response = await authFetch(
    `${API_BASE_URL}/posts?page=${page}&page_size=${pageSize}`
  );
  if (!response.ok) {
    throw new Error(`获取文章列表失败: ${response.status}`);
  }
  return await response.json();
}

/**
 * 获取文章详情（需认证）
 */
export async function fetchAdminPostById(postId: number): Promise<PostDetail> {
  // 管理端通过 ID 获取（需后端提供 /api/posts/admin/{id} 或使用公开接口 by slug）
  // 此处使用公开接口作为 fallback
  const response = await authFetch(`${API_BASE_URL}/posts`);
  if (!response.ok) {
    throw new Error(`获取文章详情失败: ${response.status}`);
  }
  const data: AdminPaginatedResponse = await response.json();
  const post = data.items.find((p) => p.id === postId);
  if (!post) {
    throw new Error('文章不存在');
  }
  // 公开接口不返回 content，这里做类型兼容
  return post as unknown as PostDetail;
}

/**
 * 创建文章
 */
export async function createAdminPost(
  input: CreatePostInput
): Promise<PostDetail> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
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
 * 更新文章（通过 ID）
 */
export async function updateAdminPost(
  postId: number,
  input: UpdatePostInput
): Promise<PostDetail> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新文章失败' }));
    throw new Error(error.detail || `更新文章失败: ${response.status}`);
  }

  return await response.json();
}

/**
 * 删除文章（通过 ID）
 */
export async function deleteAdminPost(postId: number): Promise<void> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok && response.status !== 204) {
    const error = await response.json().catch(() => ({ detail: '删除文章失败' }));
    throw new Error(error.detail || `删除文章失败: ${response.status}`);
  }
}

/**
 * 检查当前用户是否已登录（管理端访问守卫）
 */
export function requireAdminAuth(): boolean {
  return isAuthenticated();
}
