import { ref, computed } from 'vue';
import type { Conversation, ConversationState } from '../types/conversation';
import * as conversationApi from '../api/conversation';

export function useConversation() {
  const conversations = ref<Conversation[]>([]);
  const currentConversationId = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // 加载对话列表
  const loadConversations = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const list = await conversationApi.getConversations();
      conversations.value = list.map((item) => ({
        id: item.id,
        title: item.title,
        preview: item.preview,
        createTime: item.createTime,
        updateTime: item.updateTime,
        messageCount: item.messageCount,
      }));
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载对话失败';
    } finally {
      isLoading.value = false;
    }
  };

  // 创建新对话
  const createConversation = async (firstMessage?: string): Promise<Conversation | null> => {
    isLoading.value = true;
    error.value = null;
    try {
      const title = firstMessage
        ? (firstMessage.length > 20 ? firstMessage.substring(0, 20) + '...' : firstMessage)
        : '新对话';

      const result = await conversationApi.createConversation(title);
      const conversation: Conversation = {
        id: result.id,
        title: result.title,
        preview: firstMessage ? (firstMessage.length > 30 ? firstMessage.substring(0, 30) + '...' : firstMessage) : '',
        createTime: result.createTime,
        updateTime: result.updateTime,
        messageCount: 0,
      };

      conversations.value.unshift(conversation);
      currentConversationId.value = conversation.id;

      return conversation;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建对话失败';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // 首次发送消息时创建对话
  const createConversationOnFirstMessage = async (firstMessage: string): Promise<Conversation | null> => {
    return createConversation(firstMessage);
  };

  // 选择对话
  const selectConversation = (id: string) => {
    currentConversationId.value = id;
  };

  // 重置当前对话（取消选中）
  const resetCurrentConversation = () => {
    currentConversationId.value = null;
  };

  // 删除对话
  const deleteConversation = async (id: string) => {
    try {
      await conversationApi.deleteConversation(id);
      const index = conversations.value.findIndex((c) => c.id === id);
      if (index !== -1) {
        conversations.value.splice(index, 1);
        if (currentConversationId.value === id) {
          currentConversationId.value = conversations.value[0]?.id || null;
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除对话失败';
    }
  };

  // 更新对话信息
  const updateConversation = async (id: string, updates: Partial<Conversation>) => {
    try {
      const result = await conversationApi.updateConversation(id, {
        title: updates.title,
        preview: updates.preview,
        messageCount: updates.messageCount,
      });

      const conv = conversations.value.find((c) => c.id === id);
      if (conv) {
        conv.title = result.title;
        conv.preview = result.preview;
        conv.messageCount = result.messageCount;
        conv.updateTime = result.updateTime;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新对话失败';
    }
  };

  // 获取当前对话
  const currentConversation = computed(() => {
    if (!currentConversationId.value) return null;
    return conversations.value.find((c) => c.id === currentConversationId.value) || null;
  });

  return {
    conversations: computed(() => conversations.value),
    currentConversationId: computed(() => currentConversationId.value),
    currentConversation,
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    loadConversations,
    createConversation,
    createConversationOnFirstMessage,
    selectConversation,
    resetCurrentConversation,
    deleteConversation,
    updateConversation,
  };
}
