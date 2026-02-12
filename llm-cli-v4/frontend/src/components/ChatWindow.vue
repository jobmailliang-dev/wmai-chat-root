<template>
  <div class="chat-window">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <!-- 侧栏开关按钮 -->
        <button
          v-if="showSidebarToggle"
          @click="handleToggleSidebar"
          class="menu-btn"
          :title="sidebarCollapsed ? '打开侧边栏' : '关闭侧边栏'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M3 5.25C3 4.55964 3.55964 4 4.25 4H16.25C16.9404 4 17.5 4.55964 17.5 5.25C17.5 5.94036 16.9404 6.5 16.25 6.5H4.25C3.55964 6.5 3 5.94036 3 5.25ZM3 12C3 11.3096 3.55964 10.75 4.25 10.75H19.75C20.4404 10.75 21 11.3096 21 12C21 12.6904 20.4404 13.25 19.75 13.25H4.25C3.55964 13.25 3 12.6904 3 12ZM4.25 17.5C3.55964 17.5 3 18.0596 3 18.75C3 19.4404 3.55964 20 4.25 20H16.25C16.9404 20 17.5 19.4404 17.5 18.75C17.5 18.0596 16.9404 17.5 16.25 17.5H4.25Z" fill="currentColor"></path>
          </svg>
        </button>
        <h2 class="chat-title">{{ currentTitle }}</h2>
        <span v-if="state.isStreaming" class="streaming-badge">
          <span class="dot"></span>
          思考中
        </span>
      </div>
      <div class="header-right">
        <!-- <button @click="emit('clear-messages')" class="header-btn" title="清空对话">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          </svg>
        </button> -->
      </div>
    </div>

    <!-- 欢迎页面 - 空状态 -->
    <div v-if="messages.length === 0" class="welcome-screen">
      <div class="welcome-icon">🤖</div>
      <h2 class="welcome-title">有什么可以帮您的？</h2>
      <p class="welcome-subtitle">输入您的问题，开始与 AI 助手对话</p>
    </div>

    <!-- 消息列表 -->
    <MessageList v-else :messages="messages" />

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          @keydown.enter.exact.prevent="send"
          :disabled="state.isLoading || state.isStreaming"
          placeholder="输入消息..."
          rows="1"
          ref="textareaRef"
        ></textarea>
        <button
          @click="send"
          :disabled="!canSend"
          :class="['send-btn', { streaming: state.isStreaming }]"
        >
          <span v-if="state.isStreaming" class="stop-icon">⏹</span>
          <span v-else class="send-icon">➤</span>
        </button>
      </div>
      <div class="input-hint">按 Enter 发送，Shift+Enter 换行</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="state.error" class="error-toast">
      {{ state.error }}
      <button @click="emit('update-error', null)">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import MessageList from './MessageList.vue';

import type { Message } from '../types/chat';

interface Props {
  baseUrl?: string;
  messages: Message[];
  chatState: {
    isLoading: boolean;
    isStreaming: boolean;
    error: string | null;
  };
  conversationTitle?: string;
  sidebarCollapsed?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  baseUrl: 'http://localhost:8000',
  messages: () => [],
  chatState: () => ({
    isLoading: false,
    isStreaming: false,
    error: null,
  }),
  conversationTitle: '新对话',
  sidebarCollapsed: false,
});

// 响应式断点
const MOBILE_BREAKPOINT = 768;
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
const isMobile = computed(() => windowWidth.value < MOBILE_BREAKPOINT);

// 是否显示侧栏开关按钮
const showSidebarToggle = computed(() => {
  // 移动端始终显示（用于打开/关闭侧栏）
  // 桌面端折叠状态显示
  return isMobile.value || props.sidebarCollapsed;
});

// 使用 props 传入的状态
const messages = computed(() => props.messages);
const state = computed(() => props.chatState);

const inputMessage = ref('');
const textareaRef = ref<HTMLTextAreaElement>();

// 标题显示逻辑
const currentTitle = computed(() => {
  return props.conversationTitle || '新对话';
});

// 是否可以发送
const canSend = computed(() => {
  return inputMessage.value.trim() && !state.value.isLoading && !state.value.isStreaming;
});

// 更新窗口宽度
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// 发送消息
const send = async () => {
  if (!canSend.value) return;
  const message = inputMessage.value.trim();
  emit('send-message', message);
  // 如果还没有对话标题，用首条消息作为标题
  if (props.conversationTitle === '新对话' || !props.conversationTitle) {
    emit('update-title', message);
  }
  inputMessage.value = '';
};

// 切换侧栏
const handleToggleSidebar = () => {
  emit('toggle-sidebar');
};

// 聚焦输入框

// 聚焦输入框
const focusInput = () => {
  nextTick(() => {
    textareaRef.value?.focus();
  });
};

// 监听 clear-messages 事件，聚焦输入框
watch(
  () => props.messages.length,
  (newLen, oldLen) => {
    // 当消息从有变无（清空对话），聚焦输入框
    if (newLen === 0 && oldLen > 0) {
      focusInput();
    }
    // 当消息从无变有（首次发送消息），通知父组件更新标题
    if (newLen > oldLen && props.conversationTitle === '新对话') {
      const lastMsg = messages.value[newLen - 1];
      if (lastMsg.role === 'user') {
        emit('update-title', lastMsg.content);
      }
    }
  }
);

const emit = defineEmits<{
  (e: 'send-message', message: string): void;
  (e: 'clear-messages'): void;
  (e: 'update-error', error: string | null): void;
  (e: 'update-title', title: string): void;
  (e: 'toggle-sidebar'): void;
}>();

// 自动调整高度
watch(inputMessage, () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px';
  }
});

// 暴露聚焦方法给父组件
defineExpose({
  focusInput,
});
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.streaming-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #fff3cd;
  border-radius: 12px;
  font-size: 12px;
  color: #856404;
}

.streaming-badge .dot {
  width: 6px;
  height: 6px;
  background: #ffc107;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-btn {
  padding: 8px;
  background: transparent;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.header-btn:hover {
  background: #f5f5f5;
  border-color: #d0d0d0;
}

.menu-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.menu-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #333;
}

/* 欢迎页面 */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.welcome-title {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.welcome-subtitle {
  margin: 0;
  font-size: 16px;
  color: #999;
}

/* 输入区域 */
.input-area {
  padding: 16px 24px 24px;
  background: #fff;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  background: #fff;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-wrapper textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
  font-size: 15px;
  line-height: 1.5;
  max-height: 120px;
  padding: 4px 0;
  color: #333;
}

.input-wrapper textarea::placeholder {
  color: #999;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: #007aff;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: scale(1.05);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.send-btn.streaming {
  background: #ff4444;
}

.send-icon,
.stop-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-hint {
  margin-top: 8px;
  text-align: center;
  font-size: 12px;
  color: #999;
}

/* 错误提示 */
.error-toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(255, 68, 68, 0.3);
}

.error-toast button {
  background: transparent;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.error-toast button:hover {
  opacity: 0.8;
}
</style>
