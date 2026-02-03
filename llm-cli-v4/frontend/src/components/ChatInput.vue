<template>
  <div class="chat-input">
    <div class="input-container">
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
        class="send-btn"
      >
        <span v-if="state.isStreaming">⏹</span>
        <span v-else>➤</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { ChatState } from '../types/chat';

interface Props {
  state: ChatState;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'send', message: string): void;
}>();

const inputMessage = ref('');
const textareaRef = ref<HTMLTextAreaElement>();

const canSend = computed(() => {
  return inputMessage.value.trim() && !props.state.isLoading && !props.state.isStreaming;
});

const send = () => {
  if (!canSend.value) return;
  emit('send', inputMessage.value.trim());
  inputMessage.value = '';
};

// 自动调整高度
watch(inputMessage, () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px';
  }
});
</script>

<style scoped>
.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 8px 12px;
}

textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
  font-size: 14px;
  line-height: 1.5;
  max-height: 120px;
  padding: 6px 0;
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
  font-size: 16px;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
