/**
 * 认证状态管理
 * 任务码: TASK-010
 * 提供全局认证状态管理，支持登录/登出状态同步
 */

import {
  isAuthenticated,
  getUserInfo,
  getAccessToken,
  clearAuth,
  login as apiLogin,
  logout as apiLogout,
  getCurrentUser as apiGetCurrentUser,
  saveUserInfo,
  type LoginRequest,
  type UserInfo,
  type TokenResponse,
} from './auth';

// ============== 类型定义 ==============

export interface AuthState {
  isAuthenticated: boolean;
  user: UserInfo | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

type AuthListener = (state: AuthState) => void;

// ============== 状态管理类 ==============

class AuthStore {
  private state: AuthState;
  private listeners: Set<AuthListener> = new Set();

  constructor() {
    // 初始化状态，从 localStorage 读取
    this.state = {
      isAuthenticated: isAuthenticated(),
      user: getUserInfo(),
      token: getAccessToken(),
      loading: false,
      error: null,
    };
  }

  /**
   * 获取当前状态
   */
  getState(): AuthState {
    return { ...this.state };
  }

  /**
   * 订阅状态变化
   */
  subscribe(listener: AuthListener): () => void {
    this.listeners.add(listener);
    // 立即通知当前状态
    listener(this.getState());
    // 返回取消订阅函数
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 更新状态并通知所有订阅者
   */
  private setState(newState: Partial<AuthState>): void {
    this.state = { ...this.state, ...newState };
    this.listeners.forEach(listener => listener(this.getState()));
  }

  /**
   * 登录
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    this.setState({ loading: true, error: null });

    try {
      const tokenResponse = await apiLogin(credentials);

      // 获取用户信息
      const user = await apiGetCurrentUser();

      this.setState({
        isAuthenticated: true,
        user,
        token: tokenResponse.access_token,
        loading: false,
        error: null,
      });

      return tokenResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '登录失败';
      this.setState({
        loading: false,
        error: errorMessage,
      });
      throw error;
    }
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    this.setState({ loading: true });

    try {
      await apiLogout();
    } catch (error) {
      console.error('Logout error:', error);
    }

    this.setState({
      isAuthenticated: false,
      user: null,
      token: null,
      loading: false,
      error: null,
    });
  }

  /**
   * 刷新用户信息
   */
  async refreshUser(): Promise<UserInfo | null> {
    if (!this.state.isAuthenticated) {
      return null;
    }

    try {
      const user = await apiGetCurrentUser();
      this.setState({ user });
      return user;
    } catch (error) {
      console.error('Refresh user error:', error);
      // 如果获取用户信息失败，清除认证状态
      this.setState({
        isAuthenticated: false,
        user: null,
        token: null,
      });
      return null;
    }
  }

  /**
   * 清除错误
   */
  clearError(): void {
    this.setState({ error: null });
  }

  /**
   * 检查登录状态（用于页面初始化）
   */
  async checkAuth(): Promise<boolean> {
    if (!isAuthenticated()) {
      return false;
    }

    try {
      const user = await this.refreshUser();
      return user !== null;
    } catch {
      return false;
    }
  }
}

// ============== 全局实例 ==============

export const authStore = new AuthStore();

// ============== 辅助函数 ==============

/**
 * 使用认证状态的 React 风格 hook（简化版）
 * 用于在客户端脚本中获取认证状态
 */
export function useAuth(): {
  state: AuthState;
  login: (credentials: LoginRequest) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<UserInfo | null>;
} {
  return {
    state: authStore.getState(),
    login: authStore.login.bind(authStore),
    logout: authStore.logout.bind(authStore),
    refreshUser: authStore.refreshUser.bind(authStore),
  };
}

/**
 * 创建认证状态更新回调
 * 用于在组件中响应认证状态变化
 */
export function createAuthCallback(
  onLogin?: (user: UserInfo) => void,
  onLogout?: () => void,
  onError?: (error: string) => void
): AuthListener {
  return (state: AuthState) => {
    if (state.error && onError) {
      onError(state.error);
    }
    if (state.isAuthenticated && state.user && onLogin) {
      onLogin(state.user);
    }
    if (!state.isAuthenticated && onLogout) {
      onLogout();
    }
  };
}