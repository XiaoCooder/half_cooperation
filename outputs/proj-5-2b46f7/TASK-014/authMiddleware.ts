/**
 * 认证中间件模块
 * 任务码: TASK-014
 * 提供 Astro 页面级别的认证检查中间件
 */

import type { UserInfo, TokenResponse } from './auth';
import { authStateManager, type SessionState, type AuthConfig } from './authStateManager';
import { authGuard, type GuardResult, type RouteGuardConfig } from './authGuard';

// ============== 类型定义 ==============

export interface MiddlewareOptions {
  // 是否需要认证
  requireAuth?: boolean;
  // 是否需要管理员权限
  requireAdmin?: boolean;
  // 未认证时跳转路径
  redirectPath?: string;
  // 是否携带当前路径作为 redirect 参数
  carryRedirect?: boolean;
  // 认证失败回调
  onAuthFailed?: (reason: string) => void;
  // 管理员权限失败回调
  onAdminFailed?: () => void;
  // 认证成功回调
  onAuthSuccess?: (user: UserInfo) => void;
}

export interface PageAuthState {
  // 是否已认证
  isAuthenticated: boolean;
  // 是否是管理员
  isAdmin: boolean;
  // 用户信息
  user: UserInfo | null;
  // Session 信息
  session: SessionState | null;
  // 认证检查结果
  guardResult: GuardResult | null;
  // 错误信息
  error: string | null;
}

// ============== 页面认证中间件 ==============

/**
 * 创建页面认证中间件
 * 用于 Astro 页面脚本中检查认证状态
 */
export function createAuthMiddleware(options: MiddlewareOptions = {}) {
  const {
    requireAuth = true,
    requireAdmin = false,
    redirectPath = '/login',
    carryRedirect = true,
    onAuthFailed,
    onAdminFailed,
    onAuthSuccess,
  } = options;

  return {
    /**
     * 执行认证检查
     */
    check(): PageAuthState {
      const currentPath = window.location.pathname;
      const state = authStateManager.getState();

      // 检查 Session 是否有效
      if (state.session) {
        const now = Date.now();
        if (now >= state.session.expiresAt) {
          // Session 已过期
          authStateManager.clearAuth();

          const reason = 'Session expired';
          if (onAuthFailed) onAuthFailed(reason);

          if (requireAuth) {
            this.redirectToLogin(currentPath, reason);
          }

          return {
            isAuthenticated: false,
            isAdmin: false,
            user: null,
            session: null,
            guardResult: {
              allowed: false,
              redirect: carryRedirect ?
                `${redirectPath}?redirect=${encodeURIComponent(currentPath)}` :
                redirectPath,
              reason: reason,
            },
            error: reason,
          };
        }

        // Session 即将过期，刷新
        if (now > state.session.expiresAt - 5 * 60 * 1000) {
          authStateManager.refreshSession();
        }
      }

      // 未认证检查
      if (requireAuth && !state.isAuthenticated) {
        const reason = 'Not authenticated';
        if (onAuthFailed) onAuthFailed(reason);

        this.redirectToLogin(currentPath, reason);

        return {
          isAuthenticated: false,
          isAdmin: false,
          user: null,
          session: null,
          guardResult: {
            allowed: false,
            redirect: carryRedirect ?
              `${redirectPath}?redirect=${encodeURIComponent(currentPath)}` :
              redirectPath,
            reason: reason,
          },
          error: reason,
        };
      }

      // 管理员权限检查
      if (requireAdmin && !authStateManager.isAdmin()) {
        if (onAdminFailed) onAdminFailed();

        window.location.href = '/';

        return {
          isAuthenticated: state.isAuthenticated,
          isAdmin: false,
          user: state.user,
          session: state.session,
          guardResult: {
            allowed: false,
            redirect: '/',
            reason: 'Admin permission required',
          },
          error: 'Admin permission required',
        };
      }

      // 认证成功
      if (onAuthSuccess && state.user) {
        onAuthSuccess(state.user);
      }

      return {
        isAuthenticated: state.isAuthenticated,
        isAdmin: authStateManager.isAdmin(),
        user: state.user,
        session: state.session,
        guardResult: {
          allowed: true,
          user: state.user,
          session: state.session,
        },
        error: null,
      };
    },

    /**
     * 跳转到登录页
     */
    redirectToLogin(currentPath: string, reason: string): void {
      const target = carryRedirect ?
        `${redirectPath}?redirect=${encodeURIComponent(currentPath)}` :
        redirectPath;

      console.log(`[AuthMiddleware] Redirecting to login: ${reason}`);
      window.location.href = target;
    },

    /**
     * 获取认证头
     */
    getAuthHeaders(): Record<string, string> {
      const headers: Record<string, string> = {};
      const token = authStateManager.getToken();

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (authStateManager.validateCsrf(authStateManager.getCsrfToken())) {
        headers['X-CSRF-Token'] = authStateManager.getCsrfToken();
      }

      return headers;
    },

    /**
     * 带认证的 fetch
     */
    async authFetch(url: string, options: RequestInit = {}): Promise<Response> {
      const headers = new Headers(options.headers || {});
      const authHeaders = this.getAuthHeaders();

      Object.entries(authHeaders).forEach(([key, value]) => {
        headers.set(key, value);
      });

      if (!headers.has('Content-Type') && options.body) {
        headers.set('Content-Type', 'application/json');
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      // 处理 401
      if (response.status === 401) {
        authStateManager.clearAuth();
        this.redirectToLogin(window.location.pathname, 'Token expired');
      }

      return response;
    },
  };
}

// ============== 预定义中间件 ==============

/**
 * 管理页面认证中间件
 */
export const adminAuthMiddleware = createAuthMiddleware({
  requireAuth: true,
  requireAdmin: true,
  redirectPath: '/login',
  carryRedirect: true,
  onAdminFailed: () => {
    console.warn('[AdminAuth] Admin permission required');
  },
});

/**
 * 用户页面认证中间件
 */
export const userAuthMiddleware = createAuthMiddleware({
  requireAuth: true,
  requireAdmin: false,
  redirectPath: '/login',
  carryRedirect: true,
});

/**
 * 可选认证中间件（不强制跳转）
 */
export const optionalAuthMiddleware = createAuthMiddleware({
  requireAuth: false,
  requireAdmin: false,
});

// ============== Astro 页面使用示例 ==============

/**
 * 在 Astro 页面脚本中使用的认证检查函数
 */
export function usePageAuth(options: MiddlewareOptions = {}): PageAuthState {
  const middleware = createAuthMiddleware(options);
  return middleware.check();
}

/**
 * 保护管理页面的便捷函数
 */
export function protectAdminPage(): {
  user: UserInfo | null;
  session: SessionState | null;
  isAuthenticated: boolean;
} | null {
  const state = adminAuthMiddleware.check();

  if (!state.isAuthenticated || !state.isAdmin) {
    return null;
  }

  return {
    user: state.user,
    session: state.session,
    isAuthenticated: state.isAuthenticated,
  };
}

/**
 * 保护普通认证页面的便捷函数
 */
export function protectAuthPage(): {
  user: UserInfo | null;
  session: SessionState | null;
  isAuthenticated: boolean;
} | null {
  const state = userAuthMiddleware.check();

  if (!state.isAuthenticated) {
    return null;
  }

  return {
    user: state.user,
    session: state.session,
    isAuthenticated: state.isAuthenticated,
  };
}

// ============== Session 管理 ==============

/**
 * Session 管理器
 */
export const sessionManager = {
  /**
   * 创建新 Session
   */
  create(user: UserInfo): SessionState {
    authStateManager.setAuth(
      { access_token: '', refresh_token: '', token_type: 'bearer', expires_in: 1800 },
      user
    );
    return authStateManager.getSession()!;
  },

  /**
   * 获取当前 Session
   */
  get(): SessionState | null {
    return authStateManager.getSession();
  },

  /**
   * 刷新 Session
   */
  refresh(): void {
    authStateManager.refreshSession();
  },

  /**
   * 销毁 Session
   */
  destroy(): void {
    authStateManager.clearAuth();
  },

  /**
   * 检查 Session 是否有效
   */
  isValid(): boolean {
    const session = authStateManager.getSession();
    return session ? Date.now() < session.expiresAt : false;
  },

  /**
   * 获取 Session 剩余时间（秒）
   */
  getRemainingTime(): number {
    const session = authStateManager.getSession();
    if (!session) return 0;
    return Math.max(0, Math.floor((session.expiresAt - Date.now()) / 1000));
  },
};