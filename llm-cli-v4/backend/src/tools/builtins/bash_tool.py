"""Bash 工具。

在当前 shell 环境中执行命令并返回结果。
"""

import subprocess
from typing import Any, Dict

from src.tools.base import BaseTool


class BashTool(BaseTool):
    """在当前 shell 环境中执行命令的工具。"""

    def __init__(self):
        """初始化 Bash 工具。"""
        super().__init__(
            name="bash",
            description="Execute a bash command in the current shell environment and return the result",
        )

    def get_parameters(self) -> Dict[str, Any]:
        """获取参数定义。"""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute",
                },
                "description": {
                    "type": "string",
                    "description": "Brief description of what this command does (optional)",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60)",
                    "default": 60,
                },
            },
            "required": ["command"],
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行 bash 命令。"""
        command = kwargs.get('command', '')
        timeout = kwargs.get('timeout', 60)

        print(f"Bash({command})")

        if not command:
            raise ValueError("Command cannot be empty")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',  # 解决 Windows 编码问题
                timeout=timeout,
            )

            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            raise ValueError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise ValueError(f"Failed to execute command: {str(e)}")

    def __repr__(self) -> str:
        return f"BashTool(name={self.name})"
