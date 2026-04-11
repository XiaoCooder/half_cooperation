# TASK-010: 前端 - 登录页面

## 任务概述

创建 `/login` 页面，实现用户名密码表单，调用后端登录 API。

## 产出文件

| 文件名 | 说明 |
|--------|------|
| `auth.ts` | 认证 API 工具 - 登录/登出/获取用户信息 |
| `authStore.ts` | 认证状态管理 - localStorage + 状态订阅 |
| `login.astro` | 登录页面 - 科幻风格表单 |
| `me.astro` | 用户中心页面 - 显示用户信息 |

## 页面路由

| 路径 | 功能 |
|------|------|
| `/login` | 登录页面，用户名密码表单 |
| `/me` | 用户中心，显示当前用户信息 |

## 使用方法

### 1. 将文件复制到前端项目
```bash
# 复制到 TASK-009 的前端项目中
cp auth.ts ../TASK-009/src/utils/
cp authStore.ts ../TASK-009/src/utils/
cp login.astro ../TASK-009/src/pages/
cp me.astro ../TASK-009/src/pages/
```

### 2. 启动前端开发服务器
```bash
cd outputs/proj-5-2b46f7/TASK-009
npm install
npm run dev
```

### 3. 启动后端 API
```bash
cd outputs/proj-5-2b46f7/TASK-004
python main.py
```

### 4. 访问登录页面
- 前端: http://localhost:4321/login
- 后端 API: http://localhost:8000/api/auth/login

## API 接口对接

### 登录接口
```typescript
// POST /api/auth/login
// Request Body
{
  "username": "string",
  "password": "string"
}

// Response
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 获取用户信息
```typescript
// GET /api/auth/me
// Headers: Authorization: Bearer <token>

// Response
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "nickname": "Test User",
  "is_admin": false,
  "created_at": "2026-04-11T..."
}
```

### 登出接口
```typescript
// POST /api/auth/logout
// Headers: Authorization: Bearer <token>

// Response
{
  "message": "User 'testuser' logged out successfully",
  "success": true
}
```

## 功能特性

### 登录页面
- 科幻风格 UI，与博客主题一致
- 用户名/密码表单验证
- 密码显示/隐藏切换
- 加载状态动画
- 错误提示显示
- 登录成功自动跳转

### 认证工具
- localStorage 存储 token
- 自动处理 token 过期
- 支持 token 刷新
- authFetch 自动添加认证头

### 用户中心
- 显示用户详细信息
- 管理员标识
- 登出操作
- 未登录状态提示

## 配置说明

### API 基础 URL
通过环境变量配置：
```bash
# .env
PUBLIC_API_BASE_URL=/api
```

Vite 代理配置（已在 TASK-009 的 astro.config.mjs 中）：
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 测试流程

1. 启动后端 API (TASK-004)
2. 启动前端开发服务器
3. 访问 http://localhost:4321/login
4. 输入用户名密码
5. 登录成功后跳转到首页
6. 访问 http://localhost:4321/me 查看用户信息

## 注意事项

- Token 存储在 localStorage，刷新页面不会丢失
- 登录状态会自动检测，已登录用户访问登录页会跳转
- API 代理将 /api 请求转发到后端，解决 CORS 问题