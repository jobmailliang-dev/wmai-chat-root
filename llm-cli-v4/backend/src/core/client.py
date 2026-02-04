"""LLM 客户端。

核心业务逻辑，处理与 LLM API 的交互。
"""

import json
from typing import Any, Dict, List, Optional

from src.adapters.base import LLMAdapter
from src.config.models import OpenAIConfig, ToolsConfig
from src.core.session import SessionManager
from src.tools.registry import get_registry


class LLMClient:
    """LLM 客户端。"""

    def __init__(
        self,
        openai_config: OpenAIConfig,
        tools_config: ToolsConfig,
        metadata: Dict[str, str] = None,
        adapter: LLMAdapter = None,
    ):
        """初始化客户端。"""
        self.config = openai_config
        self.tools_config = tools_config
        self.metadata = metadata or {}

        # 初始化适配器
        if adapter is None:
            from src.adapters.openai import OpenAIClientAdapter
            adapter = OpenAIClientAdapter(openai_config)
        self.adapter = adapter

        # 初始化会话
        self.session = SessionManager(openai_config.system_message, self.metadata)

        # 工具配置
        self.allowed_tools = set(tools_config.allowed_tools) if tools_config.allowed_tools else set()
        self.show_tool_calls = tools_config.show_tool_calls

    def chat(self, user_message: str) -> str:
        """发送消息并获取回复（始终使用工具调用）。"""
        self.session.add_user(user_message)
        return self._chat_with_tools(user_message)

    def _chat_with_tools(self, user_message: str) -> str:
        """带工具调用的对话。"""
        from src.cli.output import print_thinking, print_message, print_tool_call, print_tool_result, print_tool_error,print_error

        registry = get_registry()
        tool_schemas = registry.get_all_schemas()
        max_iterations = self.tools_config.max_tool_calls
        iteration = 0
        final_response = ""
        skill_contexts: Dict[str, Any] = {}

        while iteration < max_iterations:
            iteration += 1

            # 过滤可用工具
            available_schemas = [
                schema for schema in tool_schemas
                if schema['function']['name'] in self.allowed_tools
            ]

            messages = self.session.get_messages()

            try:
                response = self.adapter.complete(messages=messages, tools=available_schemas)

                # 处理工具调用响应
                if isinstance(response, dict) and response.get('tool_calls'):
                    tool_calls = response['tool_calls']
                    assistant_content = response.get('content', '')
                    print_thinking(assistant_content)


                    # 添加助手消息（带工具调用）
                    self.session.add_assistant(
                        assistant_content,
                        tool_calls=[
                            {
                                "id": tc['id'],
                                "type": "function",
                                "function": {
                                    "name": tc['function']['name'],
                                    "arguments": tc['function']['arguments'],
                                },
                            }
                            for tc in tool_calls
                        ]
                    )

                    # 执行工具调用
                    for tool_call in tool_calls:
                        tool_name = tool_call['function']['name']
                        tool_args = json.loads(tool_call['function']['arguments'] or "{}")

                        if self.show_tool_calls:
                            print_tool_call(iteration, tool_name, tool_args)

                        try:
                            result = registry.execute(tool_name, **tool_args)

                            # 处理技能工具
                            if tool_name == "skill":
                                try:
                                    result_dict = json.loads(result)
                                    skill_content = result_dict.get("content", "")
                                    skill_args = result_dict.get("args", {})
                                    skill_allowed = result_dict.get("allowed_tools", [])
                                    skill_name = tool_args.get("skill_name", "unknown")

                                    skill_contexts[skill_name] = {
                                        "content": skill_content,
                                        "allowed_tools": skill_allowed,
                                    }

                                    # 合并工具列表
                                    if skill_allowed:
                                        self.allowed_tools.update(skill_allowed)

                                    # 发送成功消息
                                    self.session.add_tool_result(
                                        tool_call['id'],
                                        tool_name,
                                        f"Skill '{skill_name}' executed successfully with args: {skill_args}"
                                    )

                                    # 发送技能内容
                                    if skill_content:
                                        self.session.add_user(skill_content)
                                        if self.show_tool_calls:
                                            print_tool_result(
                                                tool_name,
                                                skill_content[:100] + ('...' if len(skill_content) > 100 else '')
                                            )

                                    continue

                                except json.JSONDecodeError:
                                    result_content = f"Failed to parse skill result: {result}"
                            else:
                                result_content = result

                            if self.show_tool_calls:
                                print_tool_result(tool_name, result_content)

                            self.session.add_tool_result(tool_call['id'], tool_name, result_content)

                        except ValueError as e:
                            error_msg = f"Tool execution error: {str(e)}"
                            if self.show_tool_calls:
                                print_tool_error(error_msg)
                            self.session.add_tool_result(tool_call['id'], tool_name, error_msg)

                    continue

                else:
                    # 最终响应
                    response_text = response if isinstance(response, str) else ""
                    if not response_text and isinstance(response, dict):
                        response_text = response.get('content', '')
                    print_message(response_text)

                    final_response = response_text
                    self.session.add_assistant(final_response)
                    break

            except Exception as e:
                final_response = f"Error in chain execution: {str(e)}"
                if self.show_tool_calls:
                    print_error(final_response)
                break
        else:
            final_response = "Maximum tool call iterations reached."
            if self.show_tool_calls:
                print_error(final_response)

        print()
        return final_response
