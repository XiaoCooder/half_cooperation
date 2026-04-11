import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  site: 'https://your-domain.com',
  output: 'static',
  srcDir: './src',
  publicDir: './public',
  outDir: './dist',
  server: {
    port: 3000,
    host: true,
  },
  vite: {
    server: {
      proxy: {
        // 开发模式下代理 API 请求到后端服务器
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    // 构建时的环境变量配置
    define: {
      'import.meta.env.PUBLIC_API_BASE_URL': JSON.stringify(process.env.PUBLIC_API_BASE_URL || '/api'),
    },
  },
});
