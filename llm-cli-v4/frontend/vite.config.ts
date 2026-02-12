import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const isMock = mode === 'mock'

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      host: true,
      proxy: isMock ? {
        '/api/chat/stream': {
          target: 'http://localhost:3002',
          ws: true,
          changeOrigin: true
        },
        '/api/health': {
          target: 'http://localhost:3002',
          changeOrigin: true
        },
        '/api/tools': {
          target: 'http://localhost:3002',
          changeOrigin: true
        }
      } : {}
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    }
  }
})
