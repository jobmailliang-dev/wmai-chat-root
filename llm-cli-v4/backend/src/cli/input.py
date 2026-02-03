"""输入处理。

处理用户输入。
"""

import sys


def get_input(prompt: str = "") -> str:
    """获取用户输入。

    Args:
        prompt: 输入提示符

    Returns:
        用户输入的字符串（去除首尾空白）
    """
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)


def is_exit_command(input_text: str, exit_cmd: str) -> bool:
    """检查是否是退出命令。"""
    return input_text.lower() == exit_cmd.lower()


def is_empty(input_text: str) -> bool:
    """检查输入是否为空。"""
    return not input_text or input_text.strip() == ""
