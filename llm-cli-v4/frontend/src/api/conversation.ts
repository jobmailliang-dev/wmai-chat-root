import type { Conversation } from '../types/conversation';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ConversationListItem {
  id: string;
  title: string;
  preview: string;
  createTime: number;
  updateTime: number;
  messageCount: number;
}

export interface ConversationMessagesResponse {
  conversationId: string;
  messages: Array<{
    id: string;
    role: string;
    content: string;
    timestamp: number;
    isThinking?: boolean;
  }>;
}

// 构建 URL
const buildUrl = (path: string, params?: Record<string, string | number | undefined>): string => {
  const url = new URL(path, API_BASE_URL);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  return url.toString();
};

// 对话列表 API
export async function getConversations(): Promise<ConversationListItem[]> {
  const response = await fetch(buildUrl('/api/conversations'));
  if (!response.ok) {
    throw new Error('获取对话列表失败');
  }
  return response.json();
}

// 创建对话
export async function createConversation(title: string): Promise<ConversationListItem> {
  const response = await fetch(buildUrl('/api/conversations', { title }), {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('创建对话失败');
  }
  return response.json();
}

// 删除对话
export async function deleteConversation(id: string): Promise<void> {
  const response = await fetch(buildUrl('/api/conversations', { id }), {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('删除对话失败');
  }
}

// 更新对话
export async function updateConversation(
  id: string,
  data: { title?: string; preview?: string; messageCount?: number }
): Promise<ConversationListItem> {
  const params: Record<string, string | number> = { id };
  if (data.title !== undefined) params.title = data.title;
  if (data.preview !== undefined) params.preview = data.preview;
  if (data.messageCount !== undefined) params.messageCount = data.messageCount;

  const response = await fetch(buildUrl('/api/conversations', params), {
    method: 'PATCH',
  });
  if (!response.ok) {
    throw new Error('更新对话失败');
  }
  return response.json();
}

// 获取对话消息
export async function getConversationMessages(conversationId: string): Promise<ConversationMessagesResponse> {
  const response = await fetch(buildUrl('/api/conversations/messages', { conversationId }));
  if (!response.ok) {
    throw new Error('获取消息失败');
  }
  return response.json();
}
