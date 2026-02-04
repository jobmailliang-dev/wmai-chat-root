"""Qwen 兼容适配器。

实现 Qwen API 的适配器，支持 OpenAI 兼容模式和 thinking 模式。
"""

from typing import Any, Dict, Generator, List

from openai import OpenAI

from src.adapters.base import LLMAdapter
from src.config.models import QwenConfig


class QwenClientAdapter(LLMAdapter):
    """Qwen API 适配器。"""

    def __init__(self, config: QwenConfig):
        """初始化适配器。"""
        self.client = OpenAI(
            base_url=config.api_url if config.api_url else None,
            api_key=config.api_key,
        )
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.use_stream = config.use_stream
        self.enable_thinking = config.enable_thinking
        self.thinking_budget = config.thinking_budget

    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """调用 Qwen API。"""
        try:
            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": False,
            }

            # Qwen 扩展参数
            if self.enable_thinking:
                request_params["extra_body"] = {
                    "enable_thinking": True,
                    "thinking_budget": self.thinking_budget,
                }

            # 只有当工具列表非空时才传递 tools 参数
            if tools:
                request_params["tools"] = tools

            response = self.client.chat.completions.create(**request_params)

            completion = response.choices[0].message

            # 处理工具调用
            if completion.tool_calls:
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
            raise ConnectionError(f"Qwen API call failed: {str(e)}")

    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """流式调用 Qwen API。

        Qwen 的流式响应包含 reasoning_content（思考过程）和 content（最终回答）。
        工具调用的 arguments 是增量返回的，需要按 index 拼接。
        """
        # 用于增量拼接工具调用参数
        tool_calls_buffer: Dict[int, Dict] = {}

        try:
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": True,
            }

            # Qwen 扩展参数
            if self.enable_thinking:
                request_params["extra_body"] = {
                    "enable_thinking": True,
                    "thinking_budget": self.thinking_budget,
                }

            # 只有当工具列表非空时才传递 tools 参数
            if tools:
                request_params["tools"] = tools

            response = self.client.chat.completions.create(**request_params)

            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    # Qwen 思考过程内容
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        yield {"reasoning_content": delta.reasoning_content}

                    # 最终回答内容
                    if delta.content:
                        yield {"content": delta.content}

                    # 工具调用 - 需要增量拼接参数
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            index = tc.index
                            if index not in tool_calls_buffer:
                                tool_calls_buffer[index] = {
                                    "id": tc.id,
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": "",
                                    },
                                }
                            # 增量拼接 arguments
                            if tc.function.arguments:
                                tool_calls_buffer[index]["function"]["arguments"] += tc.function.arguments

            # 发送所有缓冲的工具调用
            for index in sorted(tool_calls_buffer.keys()):
                yield {"tool_calls": [tool_calls_buffer[index]]}

        except Exception as e:
            raise ConnectionError(f"Qwen API call failed: {str(e)}")

    def complete_auto(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """根据配置自动选择流式或非流式调用。"""
        if self.use_stream:
            full_content = ""
            reasoning_content = ""
            tool_calls = []
            is_answering = False

            for chunk in self.complete_stream(messages, tools, **kwargs):
                if chunk.get("reasoning_content"):
                    reasoning_content += chunk["reasoning_content"]
                if chunk.get("content"):
                    if not is_answering:
                        is_answering = True
                    full_content += chunk["content"]
                if chunk.get("tool_calls"):
                    tool_calls.extend(chunk["tool_calls"])

            # 拼接思考过程和最终回答
            if reasoning_content and full_content:
                combined_content = f"{reasoning_content}\n\n{full_content}"
            elif reasoning_content:
                combined_content = reasoning_content
            else:
                combined_content = full_content

            if tool_calls:
                return {"content": combined_content, "tool_calls": tool_calls}
            return combined_content
        else:
            return self.complete(messages, tools, **kwargs)
