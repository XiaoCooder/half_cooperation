import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  site: 'https://your-domain.com',
  output: 'static',
  srcDir: './src',
  publicDir: './public',
  outDir: './dist',
});
