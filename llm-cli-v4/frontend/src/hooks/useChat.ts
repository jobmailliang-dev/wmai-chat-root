import { ref, reactive, computed } from 'vue';
import type { Message, ThinkingLog, ChatState } from '../types/chat';
import { streamRequest } from '../utils/streamRequest';

export function useChat(baseUrl = 'http://localhost:8000') {
  const messages = ref<Message[]>([]);
  const state = reactive<ChatState>({
    isLoading: false,
    isStreaming: false,
    error: null,
  });

  const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);

  const addMessage = (role: Message['role'], content: string = '') => {
    const msg: Message = {
      id: generateId(),
      role,
      content,
      timestamp: Date.now(),
      isThinking: false,
      thinkingLog: [],
    };
    messages.value.push(msg);
    return msg.id;
  };

  // SSE 事件处理
  const handleSSERecord = (eventType: string, data: string | object, msgId: string) => {
    const lastMsg = messages.value.find(m => m.id === msgId);
    if (!lastMsg) return;

    // 将 data 转换为字符串
    const dataStr = typeof data === 'string' ? data : JSON.stringify(data);

    // 记录所有 thinking/tool_call/tool_result/tool_error 事件到日志
    if (['thinking', 'tool_call', 'tool_result', 'tool_error'].includes(eventType)) {
      lastMsg.thinkingLog.push({
        timestamp: Date.now(),
        eventType,
        rawData: dataStr,
      });
      // 进入 thinking 状态
      lastMsg.isThinking = true;
    }
    console.log('variable: ', eventType);
    switch (eventType) {
      case 'content':
        // content 事件：累积内容，关闭 thinking 状态
        lastMsg.isThinking = false;
        lastMsg.content += dataStr;
        break;

      case 'thinking':
        // thinking 事件：保持 thinking 状态
        lastMsg.isThinking = true;
        break;

      case 'tool_call':
      case 'tool_result':
      case 'tool_error':
        // 工具相关事件：保持 thinking 状态
        lastMsg.isThinking = true;
        break;

      case 'done':
        // 流结束：关闭 thinking 状态和流状态
        lastMsg.isThinking = false;
        state.isLoading = false;
        state.isStreaming = false;
        break;

      case 'error':
        lastMsg.isThinking = false;
        lastMsg.content += `\n错误: ${dataStr}`;
        break;
    }
  };

  const streamMessage = async (message: string): Promise<void> => {
    if (state.isLoading || state.isStreaming) return;

    // 添加用户消息
    addMessage('user', message);
    state.isLoading = true;
    state.isStreaming = true;
    state.error = null;

    // 创建助手消息占位
    const assistantMsgId = addMessage('assistant');

    // 使用 streamRequest 工具类发起请求
    await streamRequest(
      '/api/chat/stream',
      { message },
      (event, data) => {
        handleSSERecord(event, data, assistantMsgId);
      },
      {
        method: 'GET',
        baseUrl,
        onError: (error) => {
          state.error = error.message;
          const lastMsg = messages.value.find(m => m.id === assistantMsgId);
          if (lastMsg) {
            lastMsg.content += `\n错误: ${error.message}`;
            lastMsg.isThinking = false;
          }
        },
        onComplete: () => {
          // 确保状态被重置
          state.isLoading = false;
          state.isStreaming = false;
        }
      }
    );
  };

  const clearMessages = () => {
    messages.value = [];
  };

  return {
    messages: computed(() => messages.value),
    state: computed(() => ({
      isLoading: state.isLoading,
      isStreaming: state.isStreaming,
      error: state.error,
    })),
    streamMessage,
    clearMessages,
  };
}
