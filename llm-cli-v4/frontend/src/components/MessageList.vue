<template>
  <div class="message-list" ref="containerRef">
    <div
      v-for="msg in messages"
      :key="msg.id"
      :class="['message-item', msg.role]"
    >
      <!-- AI 头像 -->
      <template v-if="msg.role === 'assistant'">
        <div class="avatar ai-avatar">
          <span class="avatar-icon">AI</span>
        </div>
      </template>

      <!-- 消息内容 -->
      <template v-if="msg.role === 'user'">
        <div class="message-bubble user-bubble">
          {{ msg.content }}
        </div>
      </template>
      <template v-else>
        <div class="ai-message">
          <!-- Content 区域：打字机效果 -->
          <div class="content-area">
            <template v-if="msg.isThinking && !msg.content">
              <div class="typing-indicator">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="typing-text">思考中...</span>
              </div>
            </template>
            <template v-else>
              <div class="ai-content">
                {{ msg.content }}
              </div>
            </template>
          </div>

          <!-- Thinking 区域：仅在 thinking 状态时显示 -->
          <div
            v-if="msg.isThinking && msg.thinkingLog.length > 0"
            class="thinking-area"
          >
            <div class="thinking-header">
              <span class="thinking-icon">&#129504;</span>
              <span>思考过程</span>
              <span class="log-count">({{ msg.thinkingLog.length }} 条)</span>
            </div>
            <div class="thinking-log">
              <div
                v-for="(log, idx) in msg.thinkingLog"
                :key="idx"
                class="log-item"
              >
                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                <span class="log-event">{{ log.eventType }}</span>
                <pre class="log-data">{{ log.rawData }}</pre>
              </div>
            </div>
          </div>

          <!-- 完成后可折叠显示思考日志 -->
          <div
            v-if="!msg.isThinking && msg.thinkingLog.length > 0"
            class="thinking-collapsed"
          >
            <details>
              <summary>查看思考过程 ({{ msg.thinkingLog.length }} 条)</summary>
              <div class="thinking-log collapsed">
                <div
                  v-for="(log, idx) in msg.thinkingLog"
                  :key="idx"
                  class="log-item"
                >
                  <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                  <span class="log-event">{{ log.eventType }}</span>
                  <pre class="log-data">{{ log.rawData }}</pre>
                </div>
              </div>
            </details>
          </div>
        </div>
      </template>

      <!-- 用户头像 -->
      <template v-if="msg.role === 'user'">
        <div class="avatar user-avatar">
          <span class="avatar-icon">U</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { Message } from '../types/chat';

const props = defineProps<{
  messages: Message[];
}>();

const containerRef = ref<HTMLElement>();

// 自动滚动到底部
watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (containerRef.value) {
        containerRef.value.scrollTop = containerRef.value.scrollHeight;
      }
    });
  }
);

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-icon {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.user-avatar {
  background: linear-gradient(135deg, #007aff 0%, #0056b3 100%);
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.user-bubble {
  background: #007aff;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Content 区域 */
.content-area {
  padding: 12px 16px;
  background: #f0f0f0;
  border-radius: 12px;
  color: #333;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.typing-indicator .dot {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator .dot:nth-child(1) { animation-delay: 0s; }
.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.typing-text {
  margin-left: 8px;
  font-size: 13px;
}

.ai-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Thinking 区域 */
.thinking-area {
  background: #1e1e2e;
  border-radius: 8px;
  overflow: hidden;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #2d2d3d;
  color: #a6accd;
  font-size: 12px;
  font-weight: 500;
}

.log-count {
  color: #666;
  font-weight: normal;
}

.thinking-log {
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
}

.log-item {
  padding: 6px 8px;
  margin-bottom: 4px;
  background: #252535;
  border-radius: 4px;
  font-size: 11px;
}

.log-time {
  color: #6c7086;
  margin-right: 8px;
}

.log-event {
  color: #89b4fa;
  font-weight: 500;
}

.log-data {
  margin: 6px 0 0 0;
  padding: 6px;
  background: #1a1a2e;
  border-radius: 4px;
  color: #a6adc8;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 10px;
}

/* 折叠状态 */
.thinking-collapsed {
  font-size: 12px;
}

.thinking-collapsed details {
  background: #f5f5f5;
  border-radius: 6px;
  padding: 6px 12px;
}

.thinking-collapsed summary {
  cursor: pointer;
  color: #666;
  list-style: none;
}

.thinking-collapsed summary::-webkit-details-marker {
  display: none;
}

.thinking-collapsed summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 6px;
  font-size: 10px;
  transition: transform 0.2s;
}

.thinking-collapsed details[open] summary::before {
  transform: rotate(90deg);
}

.thinking-collapsed .collapsed {
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}
</style>
