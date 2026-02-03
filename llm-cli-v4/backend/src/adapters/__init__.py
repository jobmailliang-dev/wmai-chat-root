"""API 适配器模块。

提供 LLM API 的适配器实现。
"""

from src.adapters.openai import OpenAIClientAdapter

__all__ = ['OpenAIClientAdapter']
