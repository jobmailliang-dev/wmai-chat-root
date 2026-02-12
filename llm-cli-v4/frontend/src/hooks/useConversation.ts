import { ref, reactive, computed } from 'vue';
import type { Conversation, ConversationState } from '../types/conversation';

// 模拟对话存储 key
const STORAGE_KEY = 'llm-cli-conversations';
const CURRENT_KEY = 'llm-cli-current-id';

export function useConversation() {
  // 从 localStorage 加载数据
  const loadFromStorage = (): Conversation[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  const conversations = ref<Conversation[]>(loadFromStorage());
  const currentConversationId = ref<string | null>(
    localStorage.getItem(CURRENT_KEY)
  );

  // 保存到 localStorage
  const saveToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.value));
    localStorage.setItem(CURRENT_KEY, currentConversationId.value || '');
  };

  const state = reactive<ConversationState>({
    conversations: conversations.value,
    currentConversationId: currentConversationId.value,
    isLoading: false,
    error: null,
  });

  // 生成预览文本
  const generatePreview = (content: string): string => {
    return content.length > 30 ? content.substring(0, 30) + '...' : content;
  };

  // 创建新对话
  const createConversation = (firstMessage?: string): Conversation => {
    const now = Date.now();
    const id = 'conv_' + now.toString(36) + Math.random().toString(36).substr(2);
    const title = firstMessage
      ? (firstMessage.length > 20 ? firstMessage.substring(0, 20) + '...' : firstMessage)
      : '新对话';

    const conversation: Conversation = {
      id,
      title,
      preview: firstMessage ? generatePreview(firstMessage) : '',
      createTime: now,
      updateTime: now,
      messageCount: firstMessage ? 1 : 0,
    };

    conversations.value.unshift(conversation);
    currentConversationId.value = id;
    saveToStorage();

    return conversation;
  };

  // 选择对话
  const selectConversation = (id: string) => {
    currentConversationId.value = id;
    saveToStorage();
  };

  // 删除对话
  const deleteConversation = (id: string) => {
    const index = conversations.value.findIndex(c => c.id === id);
    if (index !== -1) {
      conversations.value.splice(index, 1);
      if (currentConversationId.value === id) {
        currentConversationId.value = conversations.value[0]?.id || null;
      }
      saveToStorage();
    }
  };

  // 更新对话信息
  const updateConversation = (id: string, updates: Partial<Conversation>) => {
    const conv = conversations.value.find(c => c.id === id);
    if (conv) {
      Object.assign(conv, updates);
      conv.updateTime = Date.now();
      saveToStorage();
    }
  };

  // 获取当前对话
  const currentConversation = computed(() => {
    if (!currentConversationId.value) return null;
    return conversations.value.find(c => c.id === currentConversationId.value) || null;
  });

  return {
    conversations: computed(() => conversations.value),
    currentConversationId: computed(() => currentConversationId.value),
    currentConversation,
    state: computed(() => ({
      conversations: conversations.value,
      currentConversationId: currentConversationId.value,
      isLoading: state.isLoading,
      error: state.error,
    })),
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversation,
  };
}
