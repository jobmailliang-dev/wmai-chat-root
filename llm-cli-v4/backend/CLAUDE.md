[根目录](../../CLAUDE.md) > [llm-cli-v3](../) > **backend**

# Backend 模块

## 模块职责

Backend 模块是 LLM CLI V3 的核心后端服务，提供：

- **Web 服务**: FastAPI 服务，支持 SSE 流式响应
- **LLM 客户端**: 集成 OpenAI 兼容 API，处理对话和工具调用
- **工具系统**: 可扩展的工具注册和执行框架
- **技能系统**: 动态加载和执行技能内容

## 入口与启动

### 主入口

```
backend/src/__main__.py
```

支持两种运行模式：

```bash
# Web 模式（默认）
python -m src --mode web

# CLI 模式
python -m src --mode cli
```

### 目录结构

```
backend/
  src/
    __main__.py         # 应用入口
    api/                # API 路由
      chat.py           # 聊天接口（同步 + SSE 流式）
      health.py         # 健康检查
    core/               # 核心业务
      client.py         # LLM 客户端
      session.py        # 会话管理
    tools/              # 工具系统
      base.py           # 工具基类
      registry.py       # 工具注册表
      registry_init.py  # 工具注册初始化
      builtins/         # 内置工具
    skills/             # 技能系统
      executor.py       # 技能执行器
      loader.py         # 技能加载器
      parser.py         # 技能解析器
    adapters/           # LLM 适配器
      base.py           # 适配器基类
      openai.py         # OpenAI 兼容 API 适配器
    config/             # 配置管理
      loader.py         # YAML 配置加载
      models.py         # 配置模型
    cli/                # CLI 界面
      interface.py      # CLI 主界面
      input.py          # 输入处理
      output.py         # 输出格式化
    utils/              # 工具函数
      logger.py         # 日志
      frontmatter.py    # YAML frontmatter 解析
    web/                # Web 相关
      cors.py           # CORS 配置
      sse.py            # SSE 支持
```

## 对外接口

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/chat` | POST | 同步聊天接口 |
| `/chat/stream` | GET | SSE 流式聊天接口 |
| `/health` | GET | 健康检查 |

### 事件类型 (SSE)

| 事件类型 | 描述 |
|----------|------|
| `content` | AI 响应内容 |
| `tool_call` | 工具调用触发 |
| `tool_result` | 工具执行结果 |
| `tool_error` | 工具执行错误 |
| `thinking` | 思考状态 |
| `done` | 流结束 |
| `error` | 错误 |

### 工具接口

所有工具需继承 `BaseTool` 并实现：

```python
class BaseTool(ABC):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]: ...

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]: ...
```

## 关键依赖与配置

### Python 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| fastapi | >=0.109.0 | Web 框架 |
| uvicorn | >=0.27.0 | ASGI 服务器 |
| python-multipart | >=0.0.6 | 文件上传 |
| openai | >=1.0.0 | OpenAI API |
| PyYAML | >=6.0.1 | 配置解析 |
| pytz | >=2023.3 | 时区处理 |
| sse-starlette | >=1.8.0 | SSE 支持 |

### 配置模型

```python
# config/models.py
class OpenAIConfig:
    api_url: str
    api_key: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    system_message: str = "You are a helpful assistant."

class ToolsConfig:
    allowed_tools: List[str]
    max_tool_calls: int = 10
    show_tool_calls: bool = True

class CLIConfig:
    user_prefix: str = "You"
    ai_prefix: str = "AI"
    exit_command: str = "exit"
    show_system: bool = False
```

## 数据模型

### 会话消息

```python
class SessionManager:
    def add_user(self, message: str) -> None
    def add_assistant(self, content: str, tool_calls: List = None) -> None
    def add_tool_result(self, tool_call_id: str, tool_name: str, result: str) -> None
    def get_messages(self) -> List[Dict[str, str]]
```

### LLM 响应

```python
class LLMClient:
    def chat(self, user_message: str) -> str:
        """发送消息并获取回复，始终使用工具调用"""
```

## 测试与质量

### 测试覆盖

- **当前状态**: 测试覆盖较低
- **已有测试**: 仅 `data/skills/pdf/scripts/check_bounding_boxes_test.py`
- **建议补充**: core/client.py、tools/registry.py、skills/executor.py 的单元测试

### 代码质量工具

| 工具 | 配置 |
|------|------|
| black | line-length: 100, target-version: py39 |
| isort | profile: black, line_length: 100 |
| flake8 | 默认配置 |

## 常见问题 (FAQ)

**Q: 如何添加新工具？**

1. 在 `src/tools/builtins/` 创建新工具类，继承 `BaseTool`
2. 在 `src/tools/registry_init.py` 中注册工具

**Q: 如何添加新技能？**

1. 在 `data/skills/` 创建新目录
2. 添加 `SKILL.md` 文件，包含 YAML frontmatter（name, description, license）
3. 编写技能内容，支持 `{placeholder}` 占位符

**Q: 如何配置不同的 LLM 提供商？**

修改 `config.yaml` 中的 `openai.api_url` 为兼容 OpenAI API 的端点地址。

## 相关文件清单

### 核心文件

| 文件 | 职责 |
|------|------|
| `src/__main__.py` | 应用入口 |
| `src/core/client.py` | LLM 客户端核心逻辑 |
| `src/api/chat.py` | 聊天 API 路由 |
| `src/tools/registry.py` | 工具注册表 |

### 配置文件

| 文件 | 职责 |
|------|------|
| `pyproject.toml` | 项目配置、依赖、工具配置 |
| `requirements.txt` | Python 依赖列表 |
| `src/config/loader.py` | YAML 配置加载器 |

## 变更记录 (Changelog)

| 时间戳 | 操作 | 说明 |
|--------|------|------|
| 2026-02-03 11:32:16 | 初始化 | 首次生成模块 AI 上下文文档 |
