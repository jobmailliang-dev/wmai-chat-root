// 消息数据结构定义
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  isThinking: boolean;
  thinkingLog: ThinkingLog[];
}

export interface ThinkingLog {
  timestamp: number;
  eventType: string;
  rawData: string;
}

// 聊天状态定义
export interface ChatState {
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
}

// API 请求/响应定义
export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  tool_calls?: any[];
}

// SSE 事件类型
export type SSEEventType =
  | 'content'
  | 'thinking'
  | 'tool_call'
  | 'tool_result'
  | 'tool_error'
  | 'done'
  | 'error';
