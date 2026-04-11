/**
 * 管理后台文章 API 客户端测试
 * 任务码: TASK-011
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock auth module
const mockAuth = {
  getAccessToken: vi.fn(),
  isAuthenticated: vi.fn(),
  authFetch: vi.fn(),
};

vi.mock('./auth', () => mockAuth);

describe('adminPostsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('requireAdminAuth', () => {
    it('returns true when authenticated', async () => {
      mockAuth.isAuthenticated.mockReturnValue(true);
      const { requireAdminAuth } = await import('./adminPostsApi');
      expect(requireAdminAuth()).toBe(true);
    });

    it('returns false when not authenticated', async () => {
      mockAuth.isAuthenticated.mockReturnValue(false);
      const { requireAdminAuth } = await import('./adminPostsApi');
      expect(requireAdminAuth()).toBe(false);
    });
  });

  describe('fetchAdminPosts', () => {
    it('fetches posts with auth token', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        total_pages: 1,
        items: [
          { id: 1, title: 'Post 1', slug: 'post-1', is_published: true },
          { id: 2, title: 'Post 2', slug: 'post-2', is_published: false },
        ],
      };
      mockAuth.authFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { fetchAdminPosts } = await import('./adminPostsApi');
      const result = await fetchAdminPosts(1, 20);

      expect(mockAuth.authFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/posts?page=1&page_size=20')
      );
      expect(result.total).toBe(2);
      expect(result.items).toHaveLength(2);
    });

    it('throws error on failed request', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      mockAuth.authFetch.mockResolvedValue({
        ok: false,
        status: 500,
      });

      const { fetchAdminPosts } = await import('./adminPostsApi');
      await expect(fetchAdminPosts()).rejects.toThrow('获取文章列表失败: 500');
    });
  });

  describe('createAdminPost', () => {
    it('creates post with auth token', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      const mockCreated = {
        id: 1,
        title: 'New Post',
        slug: 'new-post',
        content: 'Hello',
        is_published: false,
        tags: [],
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockCreated),
      });

      const { createAdminPost } = await import('./adminPostsApi');
      const result = await createAdminPost({
        title: 'New Post',
        content: 'Hello',
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/posts'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer fake-token',
          }),
        })
      );
      expect(result.title).toBe('New Post');
    });

    it('throws error on creation failure', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Title is required' }),
      });

      const { createAdminPost } = await import('./adminPostsApi');
      await expect(
        createAdminPost({ title: '', content: '' })
      ).rejects.toThrow('Title is required');
    });
  });

  describe('updateAdminPost', () => {
    it('updates post by ID', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      const mockUpdated = { id: 1, title: 'Updated' };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockUpdated),
      });

      const { updateAdminPost } = await import('./adminPostsApi');
      const result = await updateAdminPost(1, { title: 'Updated' });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/posts/1'),
        expect.objectContaining({
          method: 'PUT',
        })
      );
      expect(result.title).toBe('Updated');
    });
  });

  describe('deleteAdminPost', () => {
    it('deletes post successfully (204)', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 204,
      });

      const { deleteAdminPost } = await import('./adminPostsApi');
      await expect(deleteAdminPost(1)).resolves.toBeUndefined();
    });

    it('throws error on delete failure', async () => {
      mockAuth.getAccessToken.mockReturnValue('fake-token');
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: 'Not authorized' }),
      });

      const { deleteAdminPost } = await import('./adminPostsApi');
      await expect(deleteAdminPost(1)).rejects.toThrow('Not authorized');
    });
  });
});
