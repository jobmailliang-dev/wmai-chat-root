"""OpenAI 兼容适配器。

实现 OpenAI 兼容 API 的适配器。
"""

from typing import Any, Dict, Generator, List

from openai import OpenAI

from src.adapters.base import LLMAdapter
from src.config.models import OpenAIConfig


class OpenAIClientAdapter(LLMAdapter):
    """OpenAI 兼容 API 适配器。"""

    def __init__(self, config: OpenAIConfig):
        """初始化适配器。"""
        self.client = OpenAI(
            base_url=config.api_url if config.api_url else None,
            api_key=config.api_key,
        )
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature

    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """调用 OpenAI 兼容 API。"""
        try:
            # 构建请求参数
            request_params = {
                'model': self.model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
                'stream': False,
            }

            # 只有当工具列表非空时才传递 tools 参数
            if tools:
                request_params['tools'] = tools

            response = self.client.chat.completions.create(**request_params)

            completion = response.choices[0].message

            # 处理工具调用
            if completion.tool_calls:
                # 返回包含工具调用的响应
                return {
                    "content": completion.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in completion.tool_calls
                    ],
                }

            return completion.content or ""

        except Exception as e:
            raise ConnectionError(f"API call failed: {str(e)}")

    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """流式调用 OpenAI 兼容 API。

        Yields:
            包含内容块或工具调用的字典
        """
        try:
            # 构建请求参数
            request_params = {
                'model': self.model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
                'stream': True,
            }

            # 只有当工具列表非空时才传递 tools 参数
            if tools:
                request_params['tools'] = tools

            response = self.client.chat.completions.create(**request_params)

            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    # 内容块
                    if delta.content:
                        yield {"content": delta.content}

                    # 工具调用
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            yield {
                                "tool_calls": [
                                    {
                                        "id": tc.id,
                                        "function": {
                                            "name": tc.function.name,
                                            "arguments": tc.function.arguments or "",
                                        },
                                    }
                                ]
                            }

        except Exception as e:
            raise ConnectionError(f"API call failed: {str(e)}")
