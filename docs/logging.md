# 接口日志模块文档

本文档介绍项目的日志系统，包括 CLI 模式日志和 Web 模式接口日志。

## 概述

项目提供两套日志系统：

| 模式 | 模块 | 用途 |
|------|------|------|
| CLI 模式 | `src/utils/logger.py` | 简单控制台日志 |
| Web 模式 | `src/utils/logging_web.py` | 结构化接口日志 |

---

## CLI 模式日志

CLI 模式使用轻量级日志封装，适合命令行交互。

### 模块结构

```
src/
└── utils/
    └── logger.py              # CLI 简单日志
```

### 使用方式

```python
from src.utils.logger import get_logger

logger = get_logger("my_module")

# 不同级别日志
logger.info("Information message")
logger.debug("Debug message")
logger.warning("Warning message")
logger.error("Error message")

# 安静模式
logger.set_quiet(True)  # 静默，不输出 info/debug
```

### 日志级别

| 级别 | 说明 |
|------|------|
| `DEBUG` | 调试信息 |
| `INFO` | 一般信息 |
| `WARNING` | 警告信息 |
| `ERROR` | 错误信息 |

### 输出示例

```
[INFO] Tool created successfully
[ERROR] Connection failed
```

---

## Web 模式接口日志

Web 模式提供结构化的 HTTP 请求/响应日志，支持控制台简洁输出和 JSON 文件存储。

### 模块结构

```
src/
├── utils/
│   └── logging_web.py        # 日志配置和工具函数
└── web/
    └── logging_middleware.py # 请求日志中间件
```

### 主要功能

- **自动记录请求/响应**：所有 HTTP 请求自动记录详细日志
- **控制台简洁输出**：便于阅读
- **JSON 文件存储**：便于后续分析处理
- **敏感信息脱敏**：自动过滤密码、API 密钥等
- **日志轮转**：按时间自动切割，保留 30 天

### 日志文件位置

- 默认日志目录：`backend/logs/`
- 日志文件：`api.log`
- 轮转策略：每天零点切割，保留 30 天

### 日志格式

#### 控制台输出示例

```
POST /api/tools -> 200 (15.23ms) [127.0.0.1]
[tool_create] id=1, body={"name":"test"}
[tool_update] id=1, body={"name":"updated"}
```

#### 日志文件输出（JSON）

```json
{"timestamp":"2026-02-09T12:00:00Z","level":"INFO","logger":"src.api","message":"POST /api/tools -> 200 (15.23ms) [127.0.0.1]"}
```

### 敏感信息脱敏

以下字段会自动脱敏：

- `password`, `passwd`, `pwd`
- `secret`, `token`
- `api_key`, `apikey`
- `access_key`, `secret_key`
- `credential`, `private_key`
- `authorization`, `auth_token`
- `refresh_token`, `client_secret`

### 使用示例

```python
from src.utils.logging_web import get_request_logger
import json

logger = get_request_logger("src.api.tools")

# 记录日志
logger.info("User action")
logger.error("Something failed")

# 记录请求体
body_str = json.dumps(request_data, ensure_ascii=False)
logger.info(f"[tool_create] id={tool_id}, body={body_str[:200]}")
```

### API 参考

#### setup_logging()

配置日志系统（Web 模式自动调用）。

```python
from src.utils.logging_web import setup_logging

logger = setup_logging(
    log_level="INFO",       # 日志级别
    console_output=True,    # 控制台输出
    file_output=True,       # 文件输出
    retention_days=30,     # 保留天数
)
```

#### get_request_logger()

获取日志器实例。

```python
from src.utils.logging_web import get_request_logger

logger = get_request_logger("src.api")
logger.info("Message")
```

#### redact_sensitive_data()

脱敏敏感数据。

```python
from src.utils.logging_web import redact_sensitive_data

safe_data = redact_sensitive_data({"password": "123456", "data": {...}})
```

### 集成说明

在 `run_web()` 中已自动集成：

1. 初始化日志系统
2. 添加 `RequestLoggingMiddleware` 中间件
3. 自动为所有请求添加 `X-Request-ID` 响应头

---

## 如何选择

```python
# CLI 模式 / 简单日志 → 用 src.utils.logger
from src.utils.logger import get_logger
logger = get_logger()
logger.info("Simple message")

# Web 模式 / 接口日志 → 用 src.utils.logging_web
from src.utils.logging_web import get_request_logger
logger = get_request_logger("src.api")
logger.info(f"[action] id={id}")
```

---

## 常见问题

### Q: 日志不输出？

检查以下几点：
1. 确保日志级别设置正确
2. 检查 `logs/` 目录是否有写入权限
3. 确认 `console_output` 和 `file_output` 参数

### Q: 如何查看实时日志？

```bash
# 查看控制台输出
python -m src --web

# 实时查看日志文件 (Linux/Mac)
tail -f backend/logs/api.log
```

### Q: 如何调整日志级别？

编辑 `src/__main__.py` 中的 `setup_logging()` 调用：

```python
logger = setup_logging(
    log_level="DEBUG",  # 更详细的日志
    ...
)
```

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-02-09 | 重命名为 logging_web.py，控制台使用简洁格式 |
| 1.1.0 | 2026-02-09 | 移除 SSE 日志 |
| 1.0.0 | 2026-02-09 | 初始版本 |
