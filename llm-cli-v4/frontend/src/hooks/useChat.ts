import { ref, reactive, computed } from 'vue';
import type { Message, ThinkingLog, ChatState } from '../types/chat';

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

  const streamMessage = async (message: string): Promise<void> => {
    if (state.isLoading || state.isStreaming) return;

    // 添加用户消息
    addMessage('user', message);
    state.isLoading = true;
    state.isStreaming = true;
    state.error = null;

    // 创建助手消息占位
    const assistantMsgId = addMessage('assistant');

    try {
      const encodedMessage = encodeURIComponent(message);
      const response = await fetch(`${baseUrl}/api/chat/stream?message=${encodedMessage}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法读取响应流');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // 按行分割，处理 SSE 格式
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEventType = '';
        let currentData = '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            // 保存上一个事件（如果有）
            if (currentEventType && currentData) {
              handleSSERecord(currentEventType, currentData, assistantMsgId);
            }
            currentEventType = line.replace('event:', '').trim();
            currentData = '';
          } else if (line.startsWith('data:')) {
            currentData += line.replace('data:', '').trim();
          }
        }

        // 保存最后一个事件
        if (currentEventType && currentData) {
          handleSSERecord(currentEventType, currentData, assistantMsgId);
        }
      }
    } catch (err: any) {
      state.error = err.message || '流式请求失败';
      const lastMsg = messages.value.find(m => m.id === assistantMsgId);
      if (lastMsg) {
        lastMsg.content += `\n错误: ${state.error}`;
        lastMsg.isThinking = false;
      }
    } finally {
      state.isLoading = false;
      state.isStreaming = false;
    }
  };

  // SSE 事件处理
  const handleSSERecord = (eventType: string, data: string, msgId: string) => {
    const lastMsg = messages.value.find(m => m.id === msgId);
    if (!lastMsg) return;

    // 记录所有 thinking/tool_call/tool_result/tool_error 事件到日志
    if (['thinking', 'tool_call', 'tool_result', 'tool_error'].includes(eventType)) {
      lastMsg.thinkingLog.push({
        timestamp: Date.now(),
        eventType,
        rawData: data,
      });
      // 进入 thinking 状态
      lastMsg.isThinking = true;
    }

    switch (eventType) {
      case 'content':
        // content 事件：累积内容，关闭 thinking 状态
        lastMsg.isThinking = false;
        lastMsg.content += data; // 累积内容，不清空
        break;

      case 'thinking':
        // thinking 事件：保持 thinking 状态，content 累积不清空
        lastMsg.isThinking = true;
        break;

      case 'tool_call':
      case 'tool_result':
      case 'tool_error':
        // 工具相关事件：保持 thinking 状态，日志已记录
        lastMsg.isThinking = true;
        // content 保持累积，不清空
        break;

      case 'done':
        // 流结束：关闭 thinking 状态
        lastMsg.isThinking = false;
        break;

      case 'error':
        lastMsg.isThinking = false;
        lastMsg.content += `\n错误: ${data}`;
        break;
    }
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
