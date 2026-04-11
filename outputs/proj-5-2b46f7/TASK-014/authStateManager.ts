/**
 * 认证状态管理模块（增强版）
 * 任务码: TASK-014
 * 支持 Cookie/Session 存储，提供更安全的认证管理
 */

import type { UserInfo, TokenResponse } from './auth';

// ============== 存储类型配置 ==============

type StorageType = 'localStorage' | 'cookie' | 'sessionStorage';

// 默认使用 localStorage，可通过配置切换
const DEFAULT_STORAGE_TYPE: StorageType = 'localStorage';

// 存储键名
const STORAGE_KEYS = {
  TOKEN: 'blog_auth_token',
  REFRESH_TOKEN: 'blog_refresh_token',
  USER_INFO: 'blog_user_info',
  SESSION_ID: 'blog_session_id',
  CSRF_TOKEN: 'blog_csrf_token',
  STORAGE_TYPE: 'blog_storage_type',
};

// ============== Cookie 工具函数 ==============

/**
 * 设置 Cookie
 */
function setCookie(name: string, value: string, options: {
  expires?: number; // 天数
  path?: string;
  domain?: string;
  secure?: boolean;
  sameSite?: 'strict' | 'lax' | 'none';
} = {}): void {
  const {
    expires = 7,
    path = '/',
    domain,
    secure = true,
    sameSite = 'lax'
  } = options;

  let cookieStr = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
  cookieStr += `; path=${path}`;

  if (expires) {
    const date = new Date();
    date.setTime(date.getTime() + expires * 24 * 60 * 60 * 1000);
    cookieStr += `; expires=${date.toUTCString()}`;
  }

  if (domain) cookieStr += `; domain=${domain}`;
  if (secure) cookieStr += '; secure';
  cookieStr += `; sameSite=${sameSite}`;

  document.cookie = cookieStr;
}

/**
 * 获取 Cookie
 */
function getCookie(name: string): string | null {
  const nameEQ = encodeURIComponent(name) + '=';
  const cookies = document.cookie.split(';');

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(nameEQ)) {
      return decodeURIComponent(cookie.substring(nameEQ.length));
    }
  }

  return null;
}

/**
 * 删除 Cookie
 */
function deleteCookie(name: string, options: {
  path?: string;
  domain?: string;
} = {}): void {
  const { path = '/', domain } = options;

  let cookieStr = `${encodeURIComponent(name)}=; path=${path}`;
  cookieStr += '; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  if (domain) cookieStr += `; domain=${domain}`;

  document.cookie = cookieStr;
}

// ============== Session 存储 ==============

/**
 * Session 状态接口
 */
export interface SessionState {
  sessionId: string;
  userId: number;
  username: string;
  createdAt: number;
  expiresAt: number;
  isAdmin: boolean;
}

/**
 * 创建 Session
 */
function createSession(userId: number, username: string, isAdmin: boolean): SessionState {
  const now = Date.now();
  const sessionId = generateSessionId();
  const expiresAt = now + 30 * 60 * 1000; // 30 分钟

  return {
    sessionId,
    userId,
    username,
    createdAt: now,
    expiresAt,
    isAdmin,
  };
}

/**
 * 生成 Session ID
 */
function generateSessionId(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * 检查 Session 是否有效
 */
function isSessionValid(session: SessionState): boolean {
  return Date.now() < session.expiresAt;
}

// ============== CSRF Token 管理 ==============

/**
 * 生成 CSRF Token
 */
function generateCsrfToken(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * 获取 CSRF Token
 */
function getCsrfToken(): string {
  let token = getFromStorage(STORAGE_KEYS.CSRF_TOKEN) as string;
  if (!token) {
    token = generateCsrfToken();
    saveToStorage(STORAGE_KEYS.CSRF_TOKEN, token);
  }
  return token;
}

/**
 * 验证 CSRF Token
 */
function validateCsrfToken(token: string): boolean {
  const storedToken = getFromStorage(STORAGE_KEYS.CSRF_TOKEN) as string;
  return storedToken === token;
}

// ============== 通用存储接口 ==============

/**
 * 获取当前存储类型
 */
function getStorageType(): StorageType {
  const storedType = localStorage.getItem(STORAGE_KEYS.STORAGE_TYPE);
  return (storedType as StorageType) || DEFAULT_STORAGE_TYPE;
}

/**
 * 设置存储类型
 */
function setStorageType(type: StorageType): void {
  localStorage.setItem(STORAGE_KEYS.STORAGE_TYPE, type);
}

/**
 * 保存数据到存储
 */
function saveToStorage(key: string, value: string | object, type?: StorageType): void {
  const storageType = type || getStorageType();
  const stringValue = typeof value === 'object' ? JSON.stringify(value) : value;

  switch (storageType) {
    case 'cookie':
      setCookie(key, stringValue);
      break;
    case 'sessionStorage':
      sessionStorage.setItem(key, stringValue);
      break;
    default:
      localStorage.setItem(key, stringValue);
  }
}

/**
 * 从存储获取数据
 */
function getFromStorage(key: string, type?: StorageType): string | object | null {
  const storageType = type || getStorageType();

  let value: string | null = null;

  switch (storageType) {
    case 'cookie':
      value = getCookie(key);
      break;
    case 'sessionStorage':
      value = sessionStorage.getItem(key);
      break;
    default:
      value = localStorage.getItem(key);
  }

  if (!value) return null;

  // 尝试解析 JSON
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

/**
 * 从存储删除数据
 */
function removeFromStorage(key: string, type?: StorageType): void {
  const storageType = type || getStorageType();

  switch (storageType) {
    case 'cookie':
      deleteCookie(key);
      break;
    case 'sessionStorage':
      sessionStorage.removeItem(key);
      break;
    default:
      localStorage.removeItem(key);
  }
}

/**
 * 清除所有认证数据
 */
function clearAllAuthData(): void {
  Object.values(STORAGE_KEYS).forEach(key => {
    // 清除所有存储类型的数据
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
    deleteCookie(key);
  });
}

// ============== 认证状态管理器 ==============

export interface AuthConfig {
  storageType: StorageType;
  tokenExpiry: number; // 秒
  sessionExpiry: number; // 秒
  csrfEnabled: boolean;
  requireAdminForProtectedRoutes: boolean;
}

const DEFAULT_CONFIG: AuthConfig = {
  storageType: 'localStorage',
  tokenExpiry: 1800, // 30 分钟
  sessionExpiry: 1800,
  csrfEnabled: true,
  requireAdminForProtectedRoutes: true,
};

/**
 * 认证管理器类
 */
export class AuthStateManager {
  private config: AuthConfig;
  private session: SessionState | null = null;
  private authState: {
    isAuthenticated: boolean;
    user: UserInfo | null;
    token: string | null;
    loading: boolean;
    error: string | null;
  };

  constructor(config: Partial<AuthConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.session = this.loadSession();
    this.authState = this.loadAuthState();
  }

  /**
   * 加载 Session
   */
  private loadSession(): SessionState | null {
    const sessionData = getFromStorage(STORAGE_KEYS.SESSION_ID);
    if (sessionData && typeof sessionData === 'object') {
      const session = sessionData as SessionState;
      if (isSessionValid(session)) {
        return session;
      }
      // Session 已过期，清除
      removeFromStorage(STORAGE_KEYS.SESSION_ID);
    }
    return null;
  }

  /**
   * 加载认证状态
   */
  private loadAuthState(): {
    isAuthenticated: boolean;
    user: UserInfo | null;
    token: string | null;
    loading: boolean;
    error: string | null;
  } {
    const token = getFromStorage(STORAGE_KEYS.TOKEN) as string | null;
    const user = getFromStorage(STORAGE_KEYS.USER_INFO) as UserInfo | null;

    return {
      isAuthenticated: token !== null && (this.session ? isSessionValid(this.session) : true),
      user,
      token,
      loading: false,
      error: null,
    };
  }

  /**
   * 设置认证信息
   */
  setAuth(tokenResponse: TokenResponse, user: UserInfo): void {
    // 保存 Token
    saveToStorage(STORAGE_KEYS.TOKEN, tokenResponse.access_token);
    saveToStorage(STORAGE_KEYS.REFRESH_TOKEN, tokenResponse.refresh_token);
    saveToStorage(STORAGE_KEYS.USER_INFO, user);

    // 创建 Session
    this.session = createSession(user.id, user.username, user.is_admin);
    saveToStorage(STORAGE_KEYS.SESSION_ID, this.session);

    // 更新状态
    this.authState = {
      isAuthenticated: true,
      user,
      token: tokenResponse.access_token,
      loading: false,
      error: null,
    };
  }

  /**
   * 清除认证信息
   */
  clearAuth(): void {
    clearAllAuthData();
    this.session = null;
    this.authState = {
      isAuthenticated: false,
      user: null,
      token: null,
      loading: false,
      error: null,
    };
  }

  /**
   * 获取认证状态
   */
  getState(): {
    isAuthenticated: boolean;
    user: UserInfo | null;
    token: string | null;
    loading: boolean;
    error: string | null;
    session: SessionState | null;
  } {
    // 检查 Session 是否过期
    if (this.session && !isSessionValid(this.session)) {
      this.clearAuth();
    }

    return {
      ...this.authState,
      session: this.session,
    };
  }

  /**
   * 获取 Token
   */
  getToken(): string | null {
    return this.authState.token;
  }

  /**
   * 获取用户信息
   */
  getUser(): UserInfo | null {
    return this.authState.user;
  }

  /**
   * 获取 Session
   */
  getSession(): SessionState | null {
    return this.session;
  }

  /**
   * 检查是否已认证
   */
  isAuthenticated(): boolean {
    return this.authState.isAuthenticated &&
           (this.session ? isSessionValid(this.session) : true);
  }

  /**
   * 检查是否是管理员
   */
  isAdmin(): boolean {
    return this.authState.user?.is_admin === true ||
           this.session?.isAdmin === true;
  }

  /**
   * 获取 CSRF Token
   */
  getCsrfToken(): string {
    return getCsrfToken();
  }

  /**
   * 验证 CSRF Token
   */
  validateCsrf(token: string): boolean {
    return validateCsrfToken(token);
  }

  /**
   * 刷新 Session
   */
  refreshSession(): void {
    if (this.authState.user) {
      this.session = createSession(
        this.authState.user.id,
        this.authState.user.username,
        this.authState.user.is_admin
      );
      saveToStorage(STORAGE_KEYS.SESSION_ID, this.session);
    }
  }

  /**
   * 检查并刷新即将过期的 Session
   */
  checkSessionExpiry(): void {
    if (this.session) {
      const now = Date.now();
      const expiryThreshold = this.session.expiresAt - 5 * 60 * 1000; // 5 分钟前刷新

      if (now >= expiryThreshold && now < this.session.expiresAt) {
        this.refreshSession();
      }
    }
  }

  /**
   * 获取存储类型
   */
  getStorageType(): StorageType {
    return this.config.storageType;
  }

  /**
   * 设置存储类型
   */
  setStorageType(type: StorageType): void {
    this.config.storageType = type;
    setStorageType(type);
  }
}

// ============== 全局实例 ==============

export const authStateManager = new AuthStateManager();

// ============== 辅助函数 ==============

/**
 * 检查认证状态并处理过期
 */
export function checkAuthStatus(): {
  isAuthenticated: boolean;
  needsRefresh: boolean;
  sessionExpired: boolean;
} {
  const state = authStateManager.getState();

  return {
    isAuthenticated: state.isAuthenticated,
    needsRefresh: state.session ?
      Date.now() > (state.session.expiresAt - 5 * 60 * 1000) : false,
    sessionExpired: state.session ? !isSessionValid(state.session) : false,
  };
}

/**
 * 获取 Authorization Header
 */
export function getAuthHeader(): Record<string, string> {
  const token = authStateManager.getToken();
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

/**
 * 获取完整的请求头（包含 CSRF）
 */
export function getSecureHeaders(): Record<string, string> {
  return {
    ...getAuthHeader(),
    'X-CSRF-Token': authStateManager.getCsrfToken(),
    'Content-Type': 'application/json',
  };
}