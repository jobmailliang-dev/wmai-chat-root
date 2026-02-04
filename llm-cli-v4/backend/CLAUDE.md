[根目录](../../CLAUDE.md) > [llm-cli-v3](../) > **backend**

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 模块职责

Backend 模块是 LLM CLI V3 的核心后端服务，提供：

- **Web 服务**: FastAPI 服务，支持 SSE 流式响应
- **LLM 客户端**: 集成 OpenAI 兼容 API，处理对话和工具调用
- **工具系统**: 可扩展的工具注册和执行框架
- **技能系统**: 动态加载和执行技能内容

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt
pip install -r requirements.txt -r pyproject.toml[dev]  # 含开发依赖

# 运行
python -m src --web    # Web 模式（默认端口 8000）
python -m src --cli    # CLI 模式
python -m src --port 8080  # 指定端口

# 代码质量
black src/             # 格式化
isort src/             # 排序导入
flake8 src/            # 代码检查
```

## 对外接口

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/chat` | POST | 同步聊天 |
| `/chat/stream` | GET | SSE 流式聊天 |
| `/health` | GET | 健康检查 |

### SSE 事件

`content`, `tool_call`, `tool_result`, `tool_error`, `thinking`, `reasoning`, `done`, `error`

## 架构概览

```
src/
├── __main__.py           # 应用入口（CLI/Web 双模式）
├── api/
│   └── chat.py           # 聊天 API（同步 + SSE）
├── core/
│   ├── client.py         # LLM 客户端，处理工具调用循环
│   └── session.py        # 会话消息管理
├── tools/
│   ├── registry.py       # 工具注册表
│   ├── base.py           # BaseTool 抽象基类
│   └── builtins/         # 内置工具（bash, calculator, datetime, read_file, skill）
├── skills/
│   ├── executor.py       # 技能执行器
│   └── loader.py         # 技能加载器（支持 YAML frontmatter）
├── adapters/
│   ├── base.py           # LLM 适配器基类
│   ├── openai.py         # OpenAI 兼容 API 适配器
│   └── qwen.py           # Qwen API 适配器
├── config/
│   ├── loader.py         # YAML 配置加载
│   └── models.py         # 配置模型
└── web/
    └── sse.py            # SSE 流式支持
```

## 添加新工具

1. 在 `src/tools/builtins/` 创建工具类，继承 `BaseTool`
2. 实现 `name`, `description`, `get_parameters()`, `execute()` 方法
3. 在 `src/tools/registry_init.py` 中注册

## 添加新技能

1. 在 `data/skills/` 创建目录，添加 `SKILL.md`
2. 包含 YAML frontmatter（name, description, license）
3. 使用 `{placeholder}` 占位符支持变量替换

## 添加新 LLM 适配器

1. 在 `src/adapters/` 创建适配器文件，如 `xxx.py`
2. 继承 `LLMAdapter` 抽象基类
3. 实现 `complete()`, `complete_stream()`, `complete_auto()` 方法
4. 在 `src/adapters/__init__.py` 中导出
5. 在 `src/config/models.py` 添加配置模型（如 `XxxConfig`）
6. 在 `src/config/loader.py` 添加解析函数
7. 在 `src/config/models.py` 的 `AppConfig` 中添加配置字段
8. 更新 `LLMClient.__init__()` 支持新的提供商

## 配置

主配置文件位于项目根目录 `config.yaml`：

```yaml
# LLM 提供商配置
llm:
  provider: qwen  # 可选: openai, qwen

# OpenAI API 配置（备选）
openai:
  api_url: "https://api.openai.com/v1"
  api_key: "your-api-key"
  model: "gpt-3.5-turbo"

# Qwen API 配置
qwen:
  api_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "your-api-key"
  model: "qwen3-14b"
  enable_thinking: false  # 启用思考模式
  thinking_budget: 4000  # 思考预算

tools:
  allowed_tools: [bash, calculator, datetime, read_file, skill]
```

## 测试

当前仅有 `data/skills/pdf/scripts/check_bounding_boxes_test.py`，核心模块缺少单元测试。

## 代码质量

- **Python**: 3.9+，双引号字符串，Google 风格 docstring
- **black**: `line-length = 100`
- **isort**: `profile = black`

## 相关文件

| 文件 | 职责 |
|------|------|
| `src/__main__.py` | 应用入口 |
| `src/core/client.py` | LLM 客户端核心 |
| `src/api/chat.py` | 聊天 API |
| `pyproject.toml` | 项目配置 |
