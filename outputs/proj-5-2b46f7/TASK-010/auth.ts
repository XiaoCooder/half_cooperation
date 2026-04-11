/**
 * 认证 API 工具
 * 任务码: TASK-010
 * 用于与后端认证 API 通信
 */

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || '/api';

// ============== 类型定义 ==============

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  nickname: string | null;
  avatar: string | null;
  bio: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface AuthError {
  error: string;
  detail: string;
}

// ============== Token 存储 ==============

const TOKEN_KEY = 'blog_access_token';
const REFRESH_TOKEN_KEY = 'blog_refresh_token';
const USER_INFO_KEY = 'blog_user_info';

/**
 * 存储 Token 到 localStorage
 */
export function saveTokens(tokenResponse: TokenResponse): void {
  localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokenResponse.refresh_token);
}

/**
 * 获取 Access Token
 */
export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * 获取 Refresh Token
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * 清除所有认证信息
 */
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_INFO_KEY);
}

/**
 * 存储 用户信息
 */
export function saveUserInfo(user: UserInfo): void {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(user));
}

/**
 * 获取 用户信息
 */
export function getUserInfo(): UserInfo | null {
  const stored = localStorage.getItem(USER_INFO_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

// ============== API 请求函数 ==============

/**
 * 用户登录
 */
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: '登录失败' }));
    throw new Error(errorData.detail || '登录失败，请检查用户名和密码');
  }

  const tokenResponse: TokenResponse = await response.json();
  saveTokens(tokenResponse);
  return tokenResponse;
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<UserInfo> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('未登录');
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearAuth();
      throw new Error('登录已过期，请重新登录');
    }
    throw new Error('获取用户信息失败');
  }

  const user: UserInfo = await response.json();
  saveUserInfo(user);
  return user;
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  const token = getAccessToken();

  if (token) {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Logout API call failed:', error);
    }
  }

  clearAuth();
}

/**
 * 刷新 Token
 */
export async function refreshToken(): Promise<TokenResponse | null> {
  const refreshTokenValue = getRefreshToken();
  if (!refreshTokenValue) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    });

    if (!response.ok) {
      clearAuth();
      return null;
    }

    const tokenResponse: TokenResponse = await response.json();
    saveTokens(tokenResponse);
    return tokenResponse;
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearAuth();
    return null;
  }
}

/**
 * 验证 Token 是否有效
 */
export async function verifyToken(): Promise<boolean> {
  const token = getAccessToken();
  if (!token) {
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    return response.ok;
  } catch {
    return false;
  }
}

/**
 * 带认证的 fetch 包装函数
 * 自动添加 Authorization header，处理 token 过期刷新
 */
export async function authFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();

  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // 如果 401，尝试刷新 token
  if (response.status === 401) {
    const newTokens = await refreshToken();
    if (newTokens) {
      // 使用新 token 重试
      headers.set('Authorization', `Bearer ${newTokens.access_token}`);
      return await fetch(url, {
        ...options,
        headers,
      });
    } else {
      // 刷新失败，清除认证状态
      clearAuth();
      throw new Error('登录已过期，请重新登录');
    }
  }

  return response;
}

/**
 * 更新用户信息
 */
export async function updateUserInfo(data: Partial<UserInfo>): Promise<UserInfo> {
  const response = await authFetch(`${API_BASE_URL}/auth/me`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('更新用户信息失败');
  }

  const user: UserInfo = await response.json();
  saveUserInfo(user);
  return user;
}