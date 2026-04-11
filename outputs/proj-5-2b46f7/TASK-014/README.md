# TASK-014: 前端 - 认证状态管理

## 任务概述

实现前端认证状态管理（Cookie/Session），保护管理页面访问。

## 产出文件

| 文件名 | 说明 |
|--------|------|
| `authStateManager.ts` | 认证状态管理器 - 支持 Cookie/Session 存储 |
| `authGuard.ts` | 认证守卫 - 路由保护和权限检查 |
| `authMiddleware.ts` | 认证中间件 - 页面级认证检查 |
| `adminGuarded.astro` | 增强版管理后台页面 - 守卫保护示例 |
| `authIndex.ts` | 认证模块集成入口 - 统一导出 |
| `test_authState.ts` | 认证状态测试 |

## 模块功能

### authStateManager.ts
- **多存储类型支持**: localStorage / Cookie / sessionStorage
- **Session 管理**: 创建、刷新、过期检测
- **CSRF Token**: 自动生成和验证
- **安全 Headers**: 自动添加认证和 CSRF 头

### authGuard.ts
- **路由匹配**: 支持精确匹配和通配符 `*`
- **权限分级**: 普通认证 / 管理员权限
- **跳转控制**: 自动跳转登录页（携带 redirect 参数）
- **状态订阅**: 认证状态变化监听

### authMiddleware.ts
- **页面级守卫**: `protectAdminPage()` / `protectAuthPage()`
- **预定义中间件**: adminAuthMiddleware / userAuthMiddleware
- **Session 管理**: 创建、刷新、销毁、有效期检查
- **认证 Fetch**: 自动添加认证头的 fetch 包装

## 使用方法

### 1. 保护管理页面
```typescript
import { protectAdminPage } from './authMiddleware';

// 在页面脚本开头
const authResult = protectAdminPage();
if (!authResult) {
  // 认证失败，已自动跳转
  return;
}
// 继续显示管理内容
```

### 2. 检查认证状态
```typescript
import { authStateManager } from './authStateManager';

// 获取认证状态
const state = authStateManager.getState();
console.log('认证:', state.isAuthenticated);
console.log('管理员:', state.isAdmin);
console.log('用户:', state.user);
```

### 3. Session 管理
```typescript
import { sessionManager } from './authMiddleware';

// 获取剩余时间
const remaining = sessionManager.getRemainingTime(); // 秒

// 刷新 Session
sessionManager.refresh();

// 销毁 Session
sessionManager.destroy();
```

### 4. 路由守卫配置
```typescript
import { authGuard } from './authGuard';

// 添加受保护路由
authGuard.addProtectedRoute('/profile');
authGuard.addAdminRoute('/admin/settings');

// 执行守卫
authGuard.enforce();
```

### 5. 安全请求
```typescript
import { authStateManager } from './authStateManager';

// 获取安全 Headers
const headers = authStateManager.getSecureHeaders();
// { Authorization: 'Bearer xxx', 'X-CSRF-Token': 'xxx' }

// 带认证的 fetch
const response = await fetch('/api/admin/posts', {
  method: 'POST',
  headers: authStateManager.getSecureHeaders(),
  body: JSON.stringify(data),
});
```

## 页面集成

### Astro 页面使用
```astro
<script>
import { protectAdminPage, sessionManager } from '../utils/authMiddleware';

// 认证守卫
const authResult = protectAdminPage();
if (!authResult) return;

// 显示用户信息
console.log('用户:', authResult.user?.username);

// Session 监控
setInterval(() => {
  const time = sessionManager.getRemainingTime();
  if (time < 300) {
    sessionManager.refresh(); // 刷新
  }
}, 30000);
</script>
```

## 功能特性

### 认证守卫
- ✅ 未认证自动跳转登录页
- ✅ 管理员权限检查
- ✅ 支持 redirect 参数回跳
- ✅ 路由通配符匹配

### Session 管理
- ✅ 30 分钟有效期
- ✅ 自动刷新（5 分钟前）
- ✅ 过期自动跳转
- ✅ 剩余时间显示

### CSRF 防护
- ✅ 自动生成 Token
- ✅ 请求自动携带
- ✅ Token 验证机制

### 多存储支持
- ✅ localStorage（默认）
- ✅ Cookie（更安全）
- ✅ sessionStorage（临时）

## 配置说明

```typescript
interface AuthConfig {
  storageType: 'localStorage' | 'cookie' | 'sessionStorage';
  tokenExpiry: number; // Token 有效期（秒）
  sessionExpiry: number; // Session 有效期（秒）
  csrfEnabled: boolean; // CSRF 防护开关
  requireAdminForProtectedRoutes: boolean;
}
```

## 注意事项

1. Session 有效期 30 分钟，页面刷新时会自动续期
2. CSRF Token 每次会话生成，请求自动携带
3. Cookie 存储更安全但需要 HTTPS
4. 管理员路由必须在 adminRoutes 中声明