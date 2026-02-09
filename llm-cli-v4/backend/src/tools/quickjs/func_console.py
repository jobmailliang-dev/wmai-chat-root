"""QuickJS 控制台函数注册模块。

提供 console.log、console.warn、console.error 等函数的注册功能。
"""


def apply(ctx, console_output_ref):
    """应用控制台函数注册到 QuickJS 上下文。

    Args:
        ctx: QuickJS 上下文
        console_output_ref: 控制台输出列表的引用
    """
    def console_log(*args):
        """console.log 实现"""
        output = " ".join(_js_value_to_string(arg) for arg in args)
        console_output_ref.append(output)
        return None

    def console_warn(*args):
        """console.warn 实现"""
        output = " ".join(_js_value_to_string(arg) for arg in args)
        console_output_ref.append(f"[WARN] {output}")
        return None

    def console_error(*args):
        """console.error 实现"""
        output = " ".join(_js_value_to_string(arg) for arg in args)
        console_output_ref.append(f"[ERROR] {output}")
        return None

    # 使用 add_callable 注册 Python 函数
    ctx.add_callable("console_log", console_log)
    ctx.add_callable("console_warn", console_warn)
    ctx.add_callable("console_error", console_error)

    # 在 JS 中定义 console 对象，调用注册的函数
    ctx.eval("""
        var console = {
            log: function(...args) { return console_log(...args); },
            warn: function(...args) { return console_warn(...args); },
            error: function(...args) { return console_error(...args); }
        };
    """)


def _js_value_to_string(value):
    """将 JS 值转换为字符串。"""
    import quickjs
    import json

    if value is None:
        return "null"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value
    elif isinstance(value, quickjs.Object):
        try:
            json_str = value.json
            if callable(json_str):
                json_str = json_str()
            return json.dumps(json_str, ensure_ascii=False)
        except Exception:
            return f"[Object: {value}]"
    else:
        return str(value)
