"""适配器基类。

定义 LLM API 适配器的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List


class LLMAdapter(ABC):
    """LLM API 适配器基类。"""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """发起 API 请求。

        Args:
            messages: 消息列表
            tools: 工具定义列表
            **kwargs: 其他参数（temperature, max_tokens 等）

        Returns:
            AI 回复内容
        """
        pass

    @abstractmethod
    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """流式发起 API 请求。

        Args:
            messages: 消息列表
            tools: 工具定义列表
            **kwargs: 其他参数（temperature, max_tokens 等）

        Yields:
            包含内容块或工具调用的字典
        """
        pass
