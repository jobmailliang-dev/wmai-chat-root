// 对话相关类型定义
export interface Conversation {
  id: string;
  title: string;
  preview: string;
  createTime: number;
  updateTime: number;
  messageCount: number;
}

export interface ConversationState {
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
}
