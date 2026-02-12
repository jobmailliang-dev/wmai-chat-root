<template>
  <div class="app-container">
    <Sidebar @new-chat="handleNewChat" @select="handleSelect" />
    <ChatWindow
      ref="chatWindowRef"
      :baseUrl="baseUrl"
      @send-message="handleSendMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import { useChat } from './hooks/useChat';
import { useConversation } from './hooks/useConversation';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const chatWindowRef = ref<InstanceType<typeof ChatWindow> | null>(null);

const { streamMessage, clearMessages } = useChat(baseUrl);
const { createConversation, selectConversation } = useConversation();

const handleNewChat = () => {
  clearMessages();
};

const handleSelect = (id: string) => {
  selectConversation(id);
  // TODO: 加载对应对话的历史消息
  clearMessages();
};

const handleSendMessage = async (message: string) => {
  await streamMessage(message);
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100%;
}

.app-container {
  display: flex;
  height: 100%;
  width: 100%;
}
</style>
