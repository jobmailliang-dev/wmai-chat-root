"""输出格式化。

处理输出格式和美化。
"""

from typing import Any, Callable, Dict, Optional


# 事件类型常量
EVENT_THINKING = "thinking"
EVENT_CONTENT = "content"
EVENT_TOOL_CALL = "tool_call"
EVENT_TOOL_RESULT = "tool_result"
EVENT_TOOL_ERROR = "tool_error"
EVENT_DONE = "done"
EVENT_ERROR = "error"


# 全局事件回调
event_callback: Optional[Callable[[str, Any], None]] = None


def set_event_callback(callback: Callable[[str, Any], None]) -> None:
    """设置全局事件回调。"""
    global event_callback
    event_callback = callback


def _trigger_event(event_type: str, data: Any) -> None:
    """触发事件回调。"""
    if event_callback:
        event_callback(event_type, data)


def print_welcome(title: str = "LLM CLI - Chat with AI", exit_cmd: str = "exit") -> None:
    """打印欢迎信息。"""
    print("=" * 60)
    print(f"{title}")
    print("=" * 60)
    print(f"Type '{exit_cmd}' to quit")
    print()


def print_thinking(content: str = "Thinking...") -> None:
    """在实时输出前打印状态信息（用于 CLI 打字机效果），灰色显示。"""
    _trigger_event(EVENT_THINKING, {"content": content})
    print(f"\x1b[90m[Thinking]  {content}\x1b[0m", end="", flush=True)


def print_message(content: str) -> None:
    """打印消息。"""
    _trigger_event(EVENT_CONTENT, {"content": content})
    print(content)


def print_error(message: str) -> None:
    """打印错误信息。"""
    _trigger_event(EVENT_ERROR, {"message": message})
    print(f"Error: {message}")


def print_tool_error(message: str) -> None:
    """打印工具错误信息。"""
    _trigger_event(EVENT_TOOL_ERROR, {"message": message})
    from src.tools.registry import get_registry
    get_registry().print_tool_error(message)


def print_tool_call(iteration: int, name: str, args: Dict[str, Any]) -> None:
    """打印工具调用信息。"""
    _trigger_event(EVENT_TOOL_CALL, {"iteration": iteration, "name": name, "args": args})
    from src.tools.registry import get_registry
    get_registry().print_tool_call(iteration, name, args)


def print_tool_result(name: str, result: str) -> None:
    """打印工具执行结果。"""
    _trigger_event(EVENT_TOOL_RESULT, {"name": name, "result": result})
    from src.tools.registry import get_registry
    get_registry().print_tool_result(name, result)

