import { createApp } from 'vue'
import App from './App.vue'

// Mock 模式日志
if (import.meta.env.VITE_USE_MOCK === 'true') {
  console.log('[Mock] 模式已启用，API 请求将发送到 mock-server')
}

createApp(App).mount('#app')
