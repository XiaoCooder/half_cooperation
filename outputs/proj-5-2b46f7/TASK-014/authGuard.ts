/**
 * 认证守卫模块
 * 任务码: TASK-014
 * 提供路由保护和认证检查功能
 */

import { authStateManager, checkAuthStatus, type SessionState } from './authStateManager';
import type { UserInfo } from './auth';

// ============== 类型定义 ==============

export interface RouteGuardConfig {
  // 需要认证的路由
  protectedRoutes: string[];
  // 需要管理员权限的路由
  adminRoutes: string[];
  // 登录页面路径
  loginPath: string;
  // 登录后默认跳转路径
  defaultRedirect: string;
  // 是否在客户端进行路由守卫
  clientSideGuard: boolean;
  // Session 过期时的处理方式
  onSessionExpired: 'redirect' | 'alert' | 'silent';
}

export interface GuardResult {
  allowed: boolean;
  redirect?: string;
  reason?: string;
  user?: UserInfo | null;
  session?: SessionState | null;
}

const DEFAULT_CONFIG: RouteGuardConfig = {
  protectedRoutes: ['/admin', '/admin/*', '/me', '/profile', '/settings'],
  adminRoutes: ['/admin', '/admin/*'],
  loginPath: '/login',
  defaultRedirect: '/',
  clientSideGuard: true,
  onSessionExpired: 'redirect',
};

// ============== 路由匹配工具 ==============

/**
 * 检查路径是否匹配模式（支持 * 通配符）
 */
function matchPattern(pattern: string, path: string): boolean {
  // 精确匹配
  if (pattern === path) return true;

  // 通配符匹配
  if (pattern.endsWith('*')) {
    const basePattern = pattern.slice(0, -1);
    return path.startsWith(basePattern);
  }

  // 起始匹配
  if (pattern.endsWith('/')) {
    return path.startsWith(pattern) || path === pattern.slice(0, -1);
  }

  return false;
}

/**
 * 检查路径是否需要认证
 */
function requiresAuth(path: string, protectedRoutes: string[]): boolean {
  return protectedRoutes.some(pattern => matchPattern(pattern, path));
}

/**
 * 检查路径是否需要管理员权限
 */
function requiresAdmin(path: string, adminRoutes: string[]): boolean {
  return adminRoutes.some(pattern => matchPattern(pattern, path));
}

// ============== 认证守卫类 ==============

export class AuthGuard {
  private config: RouteGuardConfig;
  private listeners: Set<(result: GuardResult) => void> = new Set();

  constructor(config: Partial<RouteGuardConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.initClientSideGuard();
  }

  /**
   * 初始化客户端路由守卫
   */
  private initClientSideGuard(): void {
    if (!this.config.clientSideGuard) return;

    // 监听页面加载
    window.addEventListener('DOMContentLoaded', () => {
      this.checkCurrentRoute();
    });

    // 监听路由变化（对于 SPA）
    // 注意：Astro 是 SSR/MPA，主要在页面加载时检查
  }

  /**
   * 检查当前路由
   */
  checkCurrentRoute(): GuardResult {
    const currentPath = window.location.pathname;
    return this.checkRoute(currentPath);
  }

  /**
   * 检查指定路由的访问权限
   */
  checkRoute(path: string): GuardResult {
    const state = authStateManager.getState();
    const authStatus = checkAuthStatus();

    // 不需要认证的页面直接通过
    if (!requiresAuth(path, this.config.protectedRoutes)) {
      return {
        allowed: true,
        user: state.user,
        session: state.session,
      };
    }

    // Session 过期处理
    if (authStatus.sessionExpired) {
      authStateManager.clearAuth();

      if (this.config.onSessionExpired === 'redirect') {
        return {
          allowed: false,
          redirect: this.getLoginRedirect(path),
          reason: 'Session expired',
        };
      } else if (this.config.onSessionExpired === 'alert') {
        alert('登录已过期，请重新登录');
        return {
          allowed: false,
          redirect: this.getLoginRedirect(path),
          reason: 'Session expired',
        };
      } else {
        return {
          allowed: false,
          redirect: this.getLoginRedirect(path),
          reason: 'Session expired',
        };
      }
    }

    // 未认证
    if (!state.isAuthenticated) {
      return {
        allowed: false,
        redirect: this.getLoginRedirect(path),
        reason: 'Not authenticated',
      };
    }

    // 需要管理员权限
    if (requiresAdmin(path, this.config.adminRoutes) && !authStateManager.isAdmin()) {
      return {
        allowed: false,
        redirect: this.config.defaultRedirect,
        reason: 'Admin permission required',
      };
    }

    // Session 即将过期，刷新
    if (authStatus.needsRefresh) {
      authStateManager.refreshSession();
    }

    return {
      allowed: true,
      user: state.user,
      session: state.session,
    };
  }

  /**
   * 获取登录页跳转 URL（带 redirect 参数）
   */
  getLoginRedirect(currentPath: string): string {
    const loginPath = this.config.loginPath;
    const redirectParam = encodeURIComponent(currentPath);
    return `${loginPath}?redirect=${redirectParam}`;
  }

  /**
   * 执行守卫检查并处理跳转
   */
  enforce(path?: string): boolean {
    const targetPath = path || window.location.pathname;
    const result = this.checkRoute(targetPath);

    if (!result.allowed) {
      // 通知所有监听者
      this.listeners.forEach(listener => listener(result));

      // 执行跳转
      if (result.redirect) {
        window.location.href = result.redirect;
      }
      return false;
    }

    return true;
  }

  /**
   * 订阅守卫结果
   */
  subscribe(listener: (result: GuardResult) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * 获取当前配置
   */
  getConfig(): RouteGuardConfig {
    return { ...this.config };
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<RouteGuardConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 添加受保护路由
   */
  addProtectedRoute(route: string): void {
    if (!this.config.protectedRoutes.includes(route)) {
      this.config.protectedRoutes.push(route);
    }
  }

  /**
   * 添加管理员路由
   */
  addAdminRoute(route: string): void {
    if (!this.config.adminRoutes.includes(route)) {
      this.config.adminRoutes.push(route);
      // 管理员路由也是受保护路由
      this.addProtectedRoute(route);
    }
  }

  /**
   * 检查是否可以访问管理后台
   */
  canAccessAdmin(): GuardResult {
    return this.checkRoute('/admin');
  }

  /**
   * 检查当前用户是否是管理员
   */
  isAdmin(): boolean {
    return authStateManager.isAdmin();
  }
}

// ============== 全局实例 ==============

export const authGuard = new AuthGuard();

// ============== 便捷函数 ==============

/**
 * 快速检查当前路由
 */
export function checkCurrentRoute(): GuardResult {
  return authGuard.checkCurrentRoute();
}

/**
 * 执行守卫
 */
export function enforceGuard(): boolean {
  return authGuard.enforce();
}

/**
 * 检查管理员权限
 */
export function checkAdminAccess(): boolean {
  const result = authGuard.canAccessAdmin();
  return result.allowed;
}

/**
 * 初始化页面认证守卫（用于 Astro 页面脚本）
 */
export function initAuthGuard(
  options: {
    protectedRoutes?: string[];
    adminRoutes?: string[];
    loginPath?: string;
    onGuardFailed?: (result: GuardResult) => void;
  } = {}
): void {
  // 更新配置
  if (options.protectedRoutes) {
    authGuard.updateConfig({ protectedRoutes: options.protectedRoutes });
  }
  if (options.adminRoutes) {
    authGuard.updateConfig({ adminRoutes: options.adminRoutes });
  }
  if (options.loginPath) {
    authGuard.updateConfig({ loginPath: options.loginPath });
  }

  // 添加失败回调
  if (options.onGuardFailed) {
    authGuard.subscribe(options.onGuardFailed);
  }

  // 执行守卫
  authGuard.enforce();
}

/**
 * 保护页面入口函数（用于 Astro 页面脚本开头）
 */
export function protectPage(options: {
  requireAuth?: boolean;
  requireAdmin?: boolean;
  redirectOnFail?: boolean;
} = {}): {
  isAuthenticated: boolean;
  isAdmin: boolean;
  user: UserInfo | null;
  session: SessionState | null;
} {
  const {
    requireAuth = true,
    requireAdmin = false,
    redirectOnFail = true,
  } = options;

  const state = authStateManager.getState();

  // 未认证
  if (requireAuth && !state.isAuthenticated) {
    if (redirectOnFail) {
      window.location.href = authGuard.getLoginRedirect(window.location.pathname);
    }
    return {
      isAuthenticated: false,
      isAdmin: false,
      user: null,
      session: null,
    };
  }

  // 需要管理员但不是管理员
  if (requireAdmin && !authStateManager.isAdmin()) {
    if (redirectOnFail) {
      window.location.href = '/';
    }
    return {
      isAuthenticated: state.isAuthenticated,
      isAdmin: false,
      user: state.user,
      session: state.session,
    };
  }

  // 检查 Session
  authStateManager.checkSessionExpiry();

  return {
    isAuthenticated: state.isAuthenticated,
    isAdmin: authStateManager.isAdmin(),
    user: state.user,
    session: state.session,
  };
}