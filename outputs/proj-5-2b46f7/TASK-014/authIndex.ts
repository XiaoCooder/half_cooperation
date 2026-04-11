/**
 * 认证模块集成入口
 * 任务码: TASK-014
 * 导出所有认证相关模块，便于统一导入
 */

// 从 TASK-010 导入基础认证功能
export {
  login,
  logout,
  getCurrentUser,
  getAccessToken,
  getRefreshToken,
  saveTokens,
  saveUserInfo,
  getUserInfo,
  clearAuth,
  isAuthenticated,
  refreshToken,
  verifyToken,
  authFetch,
  updateUserInfo,
  type LoginRequest,
  type TokenResponse,
  type UserInfo,
  type AuthError,
} from './auth';

// 从 TASK-010 导入认证状态管理
export {
  authStore,
  useAuth,
  createAuthCallback,
  type AuthState,
} from './authStore';

// 导出增强的认证状态管理器（TASK-014）
export {
  authStateManager,
  checkAuthStatus,
  getAuthHeader,
  getSecureHeaders,
  type AuthConfig,
  type SessionState,
  type StorageType,
} from './authStateManager';

// 导出认证守卫（TASK-014）
export {
  authGuard,
  checkCurrentRoute,
  enforceGuard,
  checkAdminAccess,
  initAuthGuard,
  protectPage,
  type RouteGuardConfig,
  type GuardResult,
} from './authGuard';

// 导出认证中间件（TASK-014）
export {
  createAuthMiddleware,
  adminAuthMiddleware,
  userAuthMiddleware,
  optionalAuthMiddleware,
  usePageAuth,
  protectAdminPage,
  protectAuthPage,
  sessionManager,
  type MiddlewareOptions,
  type PageAuthState,
} from './authMiddleware';

// ============== 快捷导入 ==============

/**
 * 认证模块快捷导入对象
 */
export const authModule = {
  // 基础功能
  login: async (username: string, password: string) => {
    const { login } = await import('./auth');
    return login({ username, password });
  },
  logout: async () => {
    const { logout } = await import('./auth');
    return logout();
  },

  // 状态管理
  get state() {
    return authStateManager.getState();
  },
  get isAuthenticated() {
    return authStateManager.isAuthenticated();
  },
  get isAdmin() {
    return authStateManager.isAdmin();
  },
  get user() {
    return authStateManager.getUser();
  },
  get session() {
    return authStateManager.getSession();
  },

  // 守卫功能
  checkRoute: (path: string) => authGuard.checkRoute(path),
  enforceGuard: () => authGuard.enforce(),

  // 中间件
  protectAdmin: () => protectAdminPage(),
  protectAuth: () => protectAuthPage(),

  // Session 管理
  refreshSession: () => sessionManager.refresh(),
  getSessionTime: () => sessionManager.getRemainingTime(),
};

// 默认导出
export default authModule;