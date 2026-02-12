<template>
  <aside class="sidebar">
    <!-- 新建对话按钮 -->
    <div class="sidebar-header">
      <button @click="handleNewChat" class="new-chat-btn">
        <span class="plus-icon">+</span>
        新建对话
      </button>
    </div>

    <!-- 对话列表 -->
    <div class="conversation-list">
      <div class="list-title">所有对话</div>
      <div
        v-for="conv in conversations"
        :key="conv.id"
        :class="['conversation-item', { active: conv.id === currentConversationId }]"
        @click="selectConversation(conv.id)"
      >
        <div class="conv-content">
          <span class="conv-icon">💬</span>
          <span class="conv-title">{{ conv.title }}</span>
        </div>
        <button
          class="delete-btn"
          @click.stop="deleteConversation(conv.id)"
          title="删除对话"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          </svg>
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="conversations.length === 0" class="empty-state">
        <span class="empty-icon">📝</span>
        <p>暂无对话</p>
        <p class="empty-hint">点击上方按钮开始新对话</p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { Conversation } from '../types/conversation';

interface Props {
  conversations: Conversation[];
  currentConversationId: string | null;
}

interface Emits {
  (e: 'new-chat'): void;
  (e: 'select', id: string): void;
  (e: 'delete', id: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const selectConversation = (id: string) => {
  emit('select', id);
};

const deleteConversation = (id: string) => {
  emit('delete', id);
};

const handleNewChat = () => {
  emit('new-chat');
};
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  background: #f7f7f8;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 12px;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #f0f0f0;
  border-color: #d0d0d0;
}

.plus-icon {
  font-size: 18px;
  font-weight: 300;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.list-title {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  padding: 8px 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 2px;
}

.conversation-item:hover {
  background: #e8e8e8;
}

.conversation-item.active {
  background: #e0e0e0;
}

.conv-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.conv-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.conv-title {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-btn {
  opacity: 0;
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #999;
  border-radius: 4px;
  transition: all 0.2s;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #ff4444;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 4px 0;
  font-size: 14px;
}

.empty-hint {
  font-size: 12px !important;
  color: #bbb;
}
</style>
