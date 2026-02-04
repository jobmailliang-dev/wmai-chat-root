"""输入处理。

处理用户输入。
支持多行输入：Ctrl+Enter 换行，Enter 发送。
"""

import sys
import os

# 检测平台
IS_WINDOWS = sys.platform == "win32"


def _is_chinese_char(char: str) -> bool:
    """检查字符是否为中文字符（包括中文标点）。"""
    code = ord(char)
    # 中文基本汉字: 4E00-9FFF
    # 中文扩展A: 3400-4DBF
    # 中文标点: 3000-303F
    return (0x4E00 <= code <= 0x9FFF or
            0x3400 <= code <= 0x4DBF or
            0x3000 <= code <= 0x303F)


def _delete_last_char(s: str) -> tuple[str, str]:
    """删除字符串最后一个字符，返回 (新字符串, 删除的字符)。"""
    if not s:
        return s, ""
    last_char = s[-1]
    return s[:-1], last_char


def get_input(prompt: str = "") -> str:
    """获取用户输入，支持多行输入。

    - Ctrl+Enter：换行
    - Enter：发送文本
    - Ctrl+C：退出

    Args:
        prompt: 输入提示符

    Returns:
        用户输入的字符串
    """
    try:
        if IS_WINDOWS:
            result = _get_input_windows(prompt)
        else:
            result = _get_input_unix(prompt)

        if is_exit_command(result, "exit"):
            raise KeyboardInterrupt

        return result

    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)


def _get_input_windows(prompt: str) -> str:
    """Windows 平台的多行输入实现。"""
    import msvcrt

    lines = []
    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
        line = ""
        while True:
            char = msvcrt.getwch()
            # 处理 Ctrl+C
            if char == "\x03":
                raise KeyboardInterrupt

            if char == "\r":  # Enter
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            elif char == "\x08":  # Backspace
                if line:
                    line, deleted_char = _delete_last_char(line)
                    # 中文字符占 2 个显示宽度，需要退格 2 次
                    if deleted_char and _is_chinese_char(deleted_char):
                        sys.stdout.write("\x08 \x08 \x08")
                    else:
                        sys.stdout.write("\x08 \x08")
                    sys.stdout.flush()
            elif char == "\x03":  # Ctrl+C
                raise KeyboardInterrupt
            elif char == "\x16":  # Ctrl+V 粘贴
                # 尝试获取剪贴板内容
                import ctypes
                try:
                    CF_UNICODETEXT = 13
                    if ctypes.windll.user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                        ctypes.windll.user32.OpenClipboard(None)
                        data = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
                        text = ctypes.windll.kernel32.GlobalLock(data)
                        if isinstance(text, int):
                            text = ctypes.windll.kernel32.GlobalUnlock(data)
                        else:
                            text = str(text)
                        ctypes.windll.user32.CloseClipboard()
                        # 逐字符输出
                        for c in text:
                            if c == "\n":
                                line += "\n"
                                sys.stdout.write("\n")
                            else:
                                line += c
                                sys.stdout.write(c)
                        sys.stdout.flush()
                except Exception:
                    pass
            elif char == "\x00":  # 功能键前缀
                # 处理特殊键
                next_char = msvcrt.getwch()
                if next_char == "S":  # Shift+Insert 或其他
                    pass
                elif next_char == "R":  # Insert
                    pass
            elif char == "\x1b":  # ESC
                return ""
            else:
                line += char
                sys.stdout.write(char)
                sys.stdout.flush()

        # Enter 发送（如果当前行或之前有内容）

        if not line and not lines:
            return ""
        if not line:
            break
        lines.append(line)
        break  # 立即发送，不等待再次 Enter

    return "\n".join(lines).rstrip("\n")


def _get_input_unix(prompt: str) -> str:
    """Unix/Linux/macOS 平台的多行输入实现。"""
    import select
    import tty
    import termios

    lines = []
    sys.stdout.write(prompt)
    sys.stdout.flush()

    # 保存终端设置
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    current_line = ""

    try:
        while True:
            # 检查是否有输入
            if select.select([sys.stdin], [], [], 0.1)[0]:
                ch = sys.stdin.read(1)

                # Ctrl+C 退出
                if ch == "\x03":
                    raise KeyboardInterrupt

                # Enter 发送
                if ch == "\n":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    if not current_line and not lines:
                        return ""
                    if not current_line:
                        break
                    lines.append(current_line)
                    current_line = ""
                    break

                # Ctrl+J 也是换行
                if ch == "\r":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    continue

                # 处理字符
                if ch == "\x7f":  # Backspace
                    if current_line:
                        current_line = current_line[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x1b":  # ESC 序列
                    seq = sys.stdin.read(2)
                    # 忽略方向键等
                else:
                    current_line += ch
                    sys.stdout.write(ch)
                    sys.stdout.flush()

        return "\n".join(lines).strip()

    finally:
        # 恢复终端设置
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def is_exit_command(input_text: str, exit_cmd: str) -> bool:
    """检查是否是退出命令。"""
    return input_text.lower() == exit_cmd.lower()


def is_empty(input_text: str) -> bool:
    """检查输入是否为空。"""
    return not input_text or input_text.strip() == ""
