# Stream Writer Util 使用指南

## 概述

`stream_writer_util.py` 提供 **SSE (Server-Sent Events)** 流式写入的异步任务支持模块。用于在异步任务中安全地将数据推送到流式响应队列，支持线程安全的写入操作。

该模块常用于：
- 工具执行过程的实时日志/进度输出
- SSE 流式 API 的异步数据推送
- 需要长时间运行的任务的流式响应

## 核心组件

| 组件 | 说明 |
|------|------|
| `task_context` | `ContextVar` 任务上下文，跨协程传递 `stream_writer` |
| `send_queue()` | 向流写入事件数据 |
| `create_queue_task()` | 创建异步任务并返回队列 |
| `MyStreamWriter` | 线程安全的流写入器类 |

## API 参考

### task_context

```python
task_context: ContextVar[dict[str, Any]]
```

任务上下文 ContextVar，用于跨协程传递流写入器实例。

```python
from src.utils.stream_writer_util import task_context

# 获取当前上下文
context = task_context.get()

# 设置上下文
task_context.set({"stream_writer": writer})
```

### send_queue()

向流写入事件数据（SSE 格式）。

```python
def send_queue(msg: Any, event: str) -> None
```

**参数：**
- `msg`: 要发送的消息数据（会被 JSON 序列化）
- `event`: 事件名称，如 `content`, `done`, `error`, `progress` 等

**示例：**
```python
from src.utils.stream_writer_util import send_queue

# 发送普通内容
send_queue({"content": "Hello"}, "content")

# 发送进度更新
send_queue({"progress": 50, "status": "处理中"}, "progress")

# 发送错误信息
send_queue({"error": "处理失败"}, "error")

# 发送完成信号
send_queue({"done": True}, "done")
```

### create_queue_task()

创建一个异步任务并返回队列，用于流式获取执行结果。

```python
def create_queue_task(
    func: Callable[..., Awaitable[R]],
    *args,
    **kwargs
) -> asyncio.Queue
```

**参数：**
- `func`: 异步函数
- `*args`: 传递给 `func` 的位置参数
- `**kwargs`: 传递给 `func` 的关键字参数

**返回：**
- `asyncio.Queue` 对象，可用于获取任务执行过程中的数据

### MyStreamWriter

线程安全的流写入器类。

```python
class MyStreamWriter:
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None
    def write(self, msg: Any) -> None
    def close(self) -> None
```

## 使用示例

### 1. FastAPI SSE 流式响应

结合 FastAPI `StreamingResponse` 实现流式 API：

```python
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.utils.stream_writer_util import create_queue_task, send_queue

router = APIRouter(prefix="/api/tools", tags=["tools"])

async def execute_tool_task(tool_name: str, params: dict):
    """工具执行任务示例。"""
    try:
        # 模拟执行步骤
        for i in range(5):
            await asyncio.sleep(0.5)
            send_queue({
                "step": i + 1,
                "progress": (i + 1) * 20,
                "message": f"执行步骤 {i + 1}..."
            }, "progress")

        # 执行完成
        send_queue({"result": "success", "output": "完成"}, "done")
    except Exception as e:
        send_queue({"error": str(e)}, "error")

@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, params: dict):
    """异步执行工具并返回流式响应。"""
    queue = create_queue_task(execute_tool_task, tool_name, params)

    async def generate_response():
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream; charset=utf-8"
    )
```

### 2. SSE 事件格式

SSE 事件格式如下：

```
event: <event_name>
data: <json_data>

```

**事件类型约定：**

| 事件名 | 说明 | 数据格式 |
|--------|------|----------|
| `content` | 文本内容块 | `{"content": "..."}` |
| `progress` | 进度更新 | `{"progress": 50, "message": "..."}` |
| `log` | 日志输出 | `{"type": "info", "message": "..."}` |
| `done` | 完成信号 | `{"result": "..."}` |
| `error` | 错误信息 | `{"error": "..."}` |

### 3. 工具执行场景

参考 `db_dynamic_tools.py` 的日志桥接模式：

```python
from src.utils.stream_writer_util import send_queue

class MyTool:
    def js_log_bridge(self, level: str, message: str):
        """供 JS 调用的日志桥接函数。"""
        send_queue({
            "type": level,
            "tool_name": self.name,
            "message": message
        }, "log")

    def _execute(self, params: dict) -> dict:
        """执行工具逻辑。"""
        self.js_log_bridge("info", "开始执行...")
        # ... 执行逻辑
        self.js_log_bridge("info", "执行完成")
        return {"success": True}
```

### 4. 自定义流写入器

直接使用 `MyStreamWriter`：

```python
import asyncio
from src.utils.stream_writer_util import MyStreamWriter

async def custom_task():
    queue = asyncio.Queue()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()

    writer = MyStreamWriter(queue, loop)

    # 在深层嵌套的逻辑中调用
    writer.write("event: content\ndata: {\"message\": \"hello\"}\n\n")
    writer.write("event: done\ndata: {\"status\": \"complete\"}\n\n")
    writer.close()

    # 消费队列
    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        print(chunk)
```

## 集成模式

### 与 ToolConfig API 集成

参考 `tool_config.py` 的异步执行接口模式：

```python
from src.utils.stream_writer_util import send_queue, create_queue_task

@router.post("/async_execute")
async def async_execute_tool(request: ToolExecuteRequest):
    """异步执行工具并流式返回结果。"""
    async def task():
        try:
            result = await tool_registry.execute_tool(
                request.tool_name,
                **request.parameters
            )
            send_queue({"type": "result", "data": result}, "end")
        except Exception as e:
            send_queue({"type": "error", "message": str(e)}, "error")

    queue = create_queue_task(task)

    async def generate():
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8"
    )
```

## 前端 SSE 消费示例

```javascript
// 使用 EventSource 消费 SSE 流
const eventSource = new EventSource('/api/tools/my_tool/execute');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

eventSource.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data);
    updateProgress(data.progress);
});

eventSource.addEventListener('done', (event) => {
    const data = JSON.parse(event.data);
    console.log('Completed:', data);
    eventSource.close();
});

eventSource.addEventListener('error', (event) => {
    const data = JSON.parse(event.data);
    console.error('Error:', data);
    eventSource.close();
});
```

## 注意事项

1. **线程安全**: `MyStreamWriter.write()` 使用 `call_soon_threadsafe`，确保在线程池中也能安全写入
2. **关闭信号**: 写入 `None` 到队列表示流结束，消费者应检查此信号
3. **JSON 序列化**: `send_queue` 自动将消息 JSON 序列化，确保数据格式正确
4. **上下文管理**: 使用 `task_context` 跨协程传递写入器，避免手动传递
