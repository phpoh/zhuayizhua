import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import fs from 'fs'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    https: {
      key: fs.readFileSync(path.resolve('/Users/hurrywang/desktop', 'server.key')),
      cert: fs.readFileSync(path.resolve('/Users/hurrywang/desktop', 'server.crt')),
    },
    host: '0.0.0.0', // 允许所有设备访问
    port: 3000, // 设置你喜欢的端口
    proxy: {
      '/api': {
        target: 'http://localhost:3000',  // 代理请求到本地服务
        changeOrigin: true, 
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
