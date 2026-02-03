<template>
  <div class="chat-window">
    <div class="chat-header">
      <h2>AI 助手</h2>
      <div :class="['status', { connected: state.isStreaming }]">
        <span class="status-dot"></span>
        {{ getStatusText() }}
      </div>
      <button @click="clearMessages" class="clear-btn">清空对话</button>
    </div>

    <MessageList :messages="messages" />

    <ChatInput :state="state" @send="handleSend" />

    <div v-if="state.error" class="error-toast">
      {{ state.error }}
      <button @click="state.error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue';
import ChatInput from './ChatInput.vue';
import { useChat } from '../hooks/useChat';

const baseUrl = 'http://localhost:8000';
const { messages, state, streamMessage, clearMessages } = useChat(baseUrl);

const handleSend = async (message: string) => {
  await streamMessage(message);
};

const getStatusText = () => {
  if (state.isStreaming) return '思考中...';
  if (state.isLoading) return '加载中...';
  return '就绪';
};
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 900px;
  margin: 0 auto;
  background: white;
  position: relative;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.status.connected .status-dot {
  background: #4caf50;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.clear-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.clear-btn:hover {
  background: #f5f5f5;
}

.error-toast {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: #ff4444;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.error-toast button {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}
</style>
