/**
 * 通用的 event-stream 请求方法
 * @param url 请求的 URL 路径（不包括基础 URL）
 * @param data 要发送的数据对象
 * @param eventHandler 处理流式数据的回调函数，接收 event 和 data 参数
 * @param options 可选的额外配置
 * @returns Promise<void>
 */
export async function streamRequest<T = any>(
  url: string,
  data: any,
  eventHandler: (event: string, data: T | string) => void,
  options: {
    method?: 'POST' | 'GET'
    customHeaders?: Record<string, string>
    baseUrl?: string
    onError?: (error: Error) => void
    onComplete?: () => void
  } = {}
): Promise<void> {
  const {
    method = 'POST',
    customHeaders = {},
    baseUrl,
    onError,
    onComplete
  } = options;

  // 获取基础 URL
  const baseURL = baseUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  try {
    // 构建请求 URL
    const requestUrl = url.startsWith('http') ? url : `${baseURL}${url}`;

    // 设置默认请求头
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      ...customHeaders
    };

    // 准备请求选项
    const fetchOptions: RequestInit = {
      method,
      headers,
    };

    // 构建请求 URL（处理 GET 查询参数）
    let finalUrl = requestUrl;
    if (method === 'GET' && data) {
      const params = new URLSearchParams();
      Object.entries(data).forEach(([key, value]) => {
        params.append(key, String(value));
      });
      finalUrl = `${requestUrl}?${params.toString()}`;
    } else if (method === 'POST') {
      fetchOptions.body = JSON.stringify(data);
    }

    // 发送请求
    const response = await fetch(finalUrl, fetchOptions);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 检查响应是否有 body
    if (!response.body) {
      throw new Error('Response body is null');
    }

    // 获取响应流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      let buffer = ''; // 用于缓存不完整的数据
      let currentEvent = ''; // 当前事件类型

      while (true) {
        const { done, value } = await reader.read();
        console.log(done, value)
        if (done) break;

        // 解码数据块并添加到缓冲区
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // 分割成行
        const lines = buffer.split('\n');

        // 保留最后一个可能不完整的行
        buffer = lines.pop() || '';

        for (const line of lines) {
          // 处理事件类型
          if (line.startsWith('event:')) {
            currentEvent = line.substring(6).trim();
          }
          // 处理数据内容
          else if (line.startsWith('data:')) {
            const dataContent = line.substring(5).trim();

            // 空数据直接触发事件（如 done 事件），非空数据尝试解析 JSON
            if (dataContent) {
              try {
                const parsed = JSON.parse(dataContent);
                eventHandler(currentEvent || 'message', parsed);
              } catch (e) {
                // 解析失败，返回原始字符串
                eventHandler(currentEvent || 'message', dataContent);
              }
            } else {
              // done 事件等空数据仍然需要触发
              eventHandler(currentEvent || 'message', dataContent);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    // 请求完成
    console.log('onComplete finish');
    
    onComplete?.();
  } catch (error) {
    console.error('Stream request failed:', error);
    onError?.(error as Error);
    throw error;
  }
}
