"""聊天 API 路由。"""

import asyncio
import json
import threading
from queue import Queue, Empty
from typing import Any, Dict, Generator, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.config.loader import load_config
from src.core.client import LLMClient
from src.cli.output import (
    EVENT_THINKING,
    EVENT_CONTENT,
    EVENT_TOOL_CALL,
    EVENT_TOOL_RESULT,
    EVENT_TOOL_ERROR,
    EVENT_DONE,
    EVENT_ERROR,
    set_event_callback,
)


class AsyncEventQueue:
    """异步事件队列，用于实时推送 SSE 事件。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._queues: Dict[str, Queue] = {}
                    cls._instance._lock = threading.Lock()
        return cls._instance

    def create_stream(self, stream_id: str) -> Queue:
        """为指定流创建队列。"""
        with self._lock:
            self._queues[stream_id] = Queue()
        return self._queues[stream_id]

    def get_queue(self, stream_id: str) -> Optional[Queue]:
        """获取指定流的队列。"""
        with self._lock:
            return self._queues.get(stream_id)

    def close_stream(self, stream_id: str) -> None:
        """关闭并清理流。"""
        with self._lock:
            if stream_id in self._queues:
                del self._queues[stream_id]

    def put_event(self, stream_id: str, event_type: str, data: Any) -> None:
        """向指定流添加事件。"""
        queue = self.get_queue(stream_id)
        if queue:
            queue.put((event_type, data))

    def put_done(self, stream_id: str) -> None:
        """标记流结束。"""
        queue = self.get_queue(stream_id)
        if queue:
            queue.put((EVENT_DONE, None))

    def get_global_callback(self):
        """获取当前全局回调（用于保存和恢复）。"""
        from src.cli.output import event_callback
        return event_callback

router = APIRouter(prefix="/chat", tags=["chat"])

# 全局客户端实例
_client: Optional[LLMClient] = None


def get_client() -> LLMClient:
    """获取或创建 LLM 客户端实例。"""
    global _client
    if _client is None:
        config = load_config()
        _client = LLMClient(
            openai_config=config.openai,
            tools_config=config.tools,
            llm_provider=config.llm_provider,
            qwen_config=config.qwen,
        )
    return _client


class ChatRequest(BaseModel):
    """聊天请求体。"""
    message: str


class ChatResponse(BaseModel):
    """聊天响应。"""
    success: bool
    response: str
    tool_calls: Optional[list] = None


@router.post("")
async def chat(request: ChatRequest) -> ChatResponse:
    """同步聊天接口。"""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        client = get_client()
        response = client.chat(request.message)
        return ChatResponse(
            success=True,
            response=response,
            tool_calls=None  # 可扩展获取工具调用历史
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to call LLM API: {str(e)}")


def event_to_sse(event_type: str, data: Any) -> str:
    """将事件转换为 SSE 格式。"""
    if event_type == EVENT_DONE:
        return "event: done\ndata:\n\n"
    elif event_type == EVENT_ERROR:
        return f"event: error\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    elif event_type == EVENT_TOOL_ERROR:
        return f"event: tool_error\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    elif event_type == EVENT_CONTENT:
        content = data.get("content", "")
        return f"event: content\ndata: {json.dumps(content, ensure_ascii=False)}\n\n"
    elif event_type == EVENT_TOOL_CALL:
        tool_data = {
            "id": data.get("iteration", 0),
            "type": "function",
            "function": {
                "name": data.get("name", ""),
                "arguments": json.dumps(data.get("args", {}), ensure_ascii=False),
            }
        }
        return f"event: tool_call\ndata: {json.dumps(tool_data, ensure_ascii=False)}\n\n"
    elif event_type == EVENT_TOOL_RESULT:
        result_data = {
            "tool_name": data.get("name", ""),
            "result": data.get("result", ""),
        }
        return f"event: tool_result\ndata: {json.dumps(result_data, ensure_ascii=False)}\n\n"
    elif event_type == EVENT_THINKING:
        return f"event: thinking\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    return ""


def _run_chat_in_thread(message: str, stream_id: str, event_queue: AsyncEventQueue):
    """在线程中运行 chat 并将事件推送到队列。"""
    original_callback = None

    def thread_collect(event_type: str, data: Any):
        event_queue.put_event(stream_id, event_type, data)

    try:
        original_callback = event_queue.get_global_callback()
        set_event_callback(thread_collect)

        client = get_client()
        client.chat(message)

    except Exception as e:
        event_queue.put_event(stream_id, EVENT_ERROR, {"message": str(e)})
    finally:
        set_event_callback(original_callback)
        event_queue.put_done(stream_id)


def generate_sse_stream(message: str):
    """生成 SSE 流（实时推送）。"""
    import uuid
    stream_id = str(uuid.uuid4())
    event_queue = AsyncEventQueue()
    queue = event_queue.create_stream(stream_id)

    # 在后台线程中运行 chat
    thread = threading.Thread(target=_run_chat_in_thread, args=(message, stream_id, event_queue), daemon=True)
    thread.start()

    try:
        while True:
            try:
                # 非阻塞获取事件，超时 1 秒
                event_type, data = queue.get(timeout=1.0)

                if event_type == EVENT_DONE:
                    yield "event: done\ndata:\n\n"
                    break

                sse_line = event_to_sse(event_type, data)
                if sse_line:
                    yield sse_line

            except Empty:
                # 超时后继续循环，保持连接活跃
                continue

    finally:
        event_queue.close_stream(stream_id)


@router.get("/stream")
async def chat_stream(message: str = Query(..., description="用户消息")):
    """SSE 流式聊天接口。"""
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return StreamingResponse(
        generate_sse_stream(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
