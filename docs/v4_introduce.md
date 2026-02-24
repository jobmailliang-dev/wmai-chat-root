---
marp: true
theme: default
paginate: true
author: "WIMI CHAT Team"
date: "2026-02-23"
title: "WIMI CHAT v4.0 - 智能对话系统产品介绍"
---

# WIMI CHAT v4.0 - 智能对话系统产品介绍

![bg opacity(0.2)](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMDAiIGN5PSIxMDAiIHI9IjkwIiBmaWxsPSJub25lIiBzdHJva2U9InJnYmEoMCwgODIsIDI1NSwgMC4zKSIgc3Ryb2tlLXdpZHRoPSIyIi8+PHBhdGggZD0iTTQwLDEwMCBDNDAsNDAgMTYwLDQwIDE2MCwxMDAgQzE2MCwxNjAgMTIwLDIwMCAyMDAsMjAwIEMyODAsMjAwIDM2MCwxNjAgMzYwLDEwMCBDMzYwLDQwIDQ4MCwwIDQ4MCwxMDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgwLDgyLDI1NSwwLjMpIiBzdHJva2Utd2lkdGg9IjIiLz48L3N2Zz4=)

**AI 驱动的下一代智能对话平台**

---

## 目录

1. [产品概述](#产品概述)
2. [核心架构](#核心架构)
3. [后端能力](#后端能力)
4. [前端界面](#前端界面)
5. [工具系统](#工具系统)
6. [技能系统](#技能系统)
7. [MCP Server 系统](#mcp-server-系统)
8. [技术特点](#技术特点)
9. [应用场景](#应用场景)

---

# 产品概述

---

## 产品定位

WIMI CHAT v4.0 是一个**支持 CLI 和 Web 双模式**的 AI 对话应用，通过集成 OpenAI 兼容 API 实现大模型支持工具调用、技能系统、SSE 语言模型交互。

| 特性 | 说明 |
|------|------|
| **双模式运行** | CLI 命令行 + Web 浏览器双模式 |
| **流式响应** | SSE (Server-Sent Events) 实时流式输出 |
| **工具调用** | 结构化的工具执行能力 |
| **技能系统** | 预定义上下文内容动态加载 |

---

## 版本演进

| 版本 | 主要特性 |
|------|----------|
| v1.x | 基础对话功能 |
| v2.x | CLI 模式优化 |
| v3.x | Web 界面引入 |
| **v4.0** | **工具系统 + 技能系统 + 完整双端架构** |

---

# 核心架构

---

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        WIMI CHAT v4.0                           │
├───────────────────────┬─────────────────────────────────────────┤
│     Backend Master    │        Frontend Master                         │
│  ┌────────────────┐   │  ┌──────────────────┬──────────────────┐ │
│  │   FastAPI      │   │  │  Vue 3 Chat      │ Vue 3 Settings   │ │
│  │   - REST API   │   │  │  - 聊天界面       │ - 工具管理       │ │
│  │   - SSE Stream │   │  │  - 对话管理       │ - 配置管理       │ │
│  │   - 工具注册表   │   │  │  - 消息流式接收   │                  │ │
│  │   - 技能执行器   │   │  └──────────────────┴──────────────────┘ │
│  │   - LLM 适配器   │   │                                         │
│  └────────────────┘   │                前端应用层                     │
│       │               │                                         │
│  ┌────▼────┐          │  ┌──────────────────┬──────────────────┐ │
│  │  SQLite │          │  │  hooks模式        │  Pinia状态管理    │ │
│  │  (数据层)  │          │  │  useChat        │  useStore        │ │
│  └─────────┘          │  │  useConversation │                  │ │
│                       │  └──────────────────┴──────────────────┘ │
│    后端服务层              │                前端逻辑层               │
└───────────────────────┴─────────────────────────────────────────┘
                              │
                    HTTP/SSE 协议
                              │
                    ┌───────────────┐
                    │   LLM-API     │
                    │  OpenAI/Qwen  │
                    └───────────────┘
```

---

## 双端架构

### 后端 (backend-master/backend)
- **框架**: FastAPI + Uvicorn
- **语言**: Python 3.9+
- **数据库**: SQLite
- **职责**: API 服务、LLM 交互、工具执行、技能加载

### 前端 (frontend-master)
- **聊天前端**: `frontend_chat` - Vue 3 聊天界面
- **设置前端**: `frontend_settings` - Vue 3 配置管理
- **构建工具**: Vite 4.5
- **UI 库**: Element Plus

---

# 后端能力

---

## API 接口概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api-chat` | POST | 同步聊天接口 |
| `/api/chat/stream` | GET | SSE 流式聊天接口 |
| `/api/conversations` | GET/POST/DELETE/PATCH | 对话管理 |
| `/api/conversations/messages` | GET/POST | 消息管理 |
| `/api/tools` | GET/POST/PUT/DELETE | 工具管理 |
| `/api/tools/execute` | POST | 工具执行 |
| `/api/tools/execute/stream` | POST | 流式工具执行 |
| `/api/health` | GET | 健康检查 |

---

## 核心模块结构

```
backend/src/
├── api/                  # API 路由层
│   ├── chat.py          # 聊天 API (同步 + SSE)
│   ├── conversations.py # 对话管理 API
│   ├── tools.py         # 工具管理 API
│   └── models.py        # 通用 API 模型
├── core/                # 核心业务逻辑
│   ├── client.py        # LLM 客户端 (工具调用循环)
│   └── session.py       # 会话管理
├── tools/               # 工具系统
│   ├── registry.py      # 工具注册表
│   ├── base.py          # 工具基类
│   └── builtins/        # 内置工具
├── skills/              # 技能系统
│   ├── loader.py        # 技能加载器
│   ├── executor.py      # 技能执行器
│   └── parser.py        # 技能解析器
├── adapters/            # LLM 适配器
│   ├── openai.py        # OpenAI 适配器
│   └── qwen.py          # Qwen 适配器
├── config/              # 配置管理
│   ├── loader.py        # 配置加载器
│   └── models.py        # 配置模型
└── modules/             # 业务模块 (依赖注入)
    ├── datasource/      # 数据库连接
    └── tools/           # 工具业务模块
```

---

## LLM 客户端核心逻辑

```python
class LLMClient:
    def _chat_with_tools(self, user_message: str) -> str:
        """带工具调用的对话 - 循环执行直到获得最终响应"""

        while iteration < max_iterations:
            # 1. 过滤可用工具
            available_schemas = filter_tools(allowed_tools)

            # 2. 调用 LLM API
            response = adapter.complete_auto(
                messages=self.session.get_messages(),
                tools=available_schemas
            )

            # 3. 处理工具调用
            if tool_calls := response.tool_calls:
                for tool_call in tool_calls:
                    # 执行工具
                    result = registry.execute(
                        tool_call['function']['name'],
                        **tool_args
                    )
                    # 添加工具结果到会话
                    self.session.add_tool_result(...)
                continue  # 继续循环

            # 4. 返回最终响应
            else:
                return response.content
```

---

# 前端界面

---

## 聊天前端功能

### 核心组件

| 组件 | 功能 |
|------|------|
| **App.vue** | 应用根组件，集成侧边栏、聊天窗口、设置弹窗 |
| **ChatWindow.vue** | 聊天主窗口，包含头部、消息列表、输入区 |
| **MessageList.vue** | 消息列表组件，展示用户和 AI 对话内容 |
| **Sidebar.vue** | 侧边栏组件，管理对话列表 |
| **SettingsDialog.vue** | 设置对话框 |

### UI 特性

- **响应式布局**: 移动端断点 768px，侧边栏可折叠
- **消息气泡**: 区分用户和 AI 消息样式
- **流式打字机效果**: 实时显示 AI 回复
- **思考过程可视化**: 显示工具调用和中间过程
- **自动滚动**: 新消息自动滚动到视图底部

---

## 设置前端功能

### 路由结构

| 路径 | 页面 | 功能 |
|------|------|------|
| `/home` | 首页 | 项目概览 |
| `/workbench` | 工作台 | 核心功能入口 |
| `/tools` | 工具管理 | 工具列表与管理 |
| `/tools/edit` | 新建工具 | 创建新工具 |
| `/tools/edit/:id` | 编辑工具 | 修改工具配置 |

### 工具管理功能

- **工具列表**: 展示所有工具卡片
- **新建工具**: 创建自定义工具
- **编辑工具**: 修改工具代码和参数
- **删除工具**: 移除不需要的工具
- **启用/禁用**: 控制工具可用性
- **导入/导出**: 批量工具数据迁移
- **工具调试**: 实时测试工具执行

---

## 前端技术栈

### 聊天前端 (frontend_chat)

- **Vue 3.3.8** + **TypeScript 5.2** + **Composition API**
- **Vite 4.5** 构建工具
- **Element Plus 2.4.2** UI 组件库
- **无 Router**: 单页面组件切换模式
- **Hooks 模式**: useChat, useConversation 状态管理

### 设置前端 (frontend_settings)

- **Vue 3.3.8** + **TypeScript 5.2**
- **Vite 4.5** 构建工具
- **Vue Router 4**: 前端路由管理
- **Pinia 2.1.7**: 状态管理
- **Element Plus 2.4.2** UI 组件库

---

# 工具系统

---

## 工具系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    工具注册中心                           │
│              src/tools/registry.py                       │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼───────┐ ┌────▼────────────┐
│ 内置工具池      │ │ 动态工具池       │
│ (builtins/)   │ │ (从数据库加载)    │
└───────────────┘ └─────────────────┘
        │               │
        └───────┬───────┘
                │
        ┌───────▼───────┐
│   LLM 调用工具时       │
│   注册中心执行对应工具   │
└───────────────────────┘
```

---

## 内置工具列表

| 工具名称 | 功能描述 | 典型场景 |
|----------|----------|----------|
| **bash** | 执行 Bash 命令 | 文件操作、系统命令执行 |
| **calculator** | 计算器 | 数学计算 |
| **datetime** | 日期时间操作 | 获取当前时间、时间计算 |
| **read_file** | 读取文件 | 读取配置文件、文档内容 |
| **skill** | 技能调用 | 执行预定义技能 |
| **quickjs** | JavaScript 执行 | 动态脚本执行 |
| **http** | HTTP 请求 | 外部 API 调用 |
| **js_dynamic** | 动态 JS 工具 | 自定义 JavaScript 逻辑 |

---

## 工具定义格式

```typescript
interface ToolDefinition {
  id: number;                    // 工具唯一标识
  name: string;                  // 工具名称
  description: string;           // 工具描述
  code: string;                  // 执行代码 (JavaScript)
  params_schema?: object;        // 参数 JSON Schema
  is_active: boolean;            // 是否启用
  inherit_from?: number;         // 继承的工具 ID
  created_at: string;            // 创建时间
  updated_at: string;            // 更新时间
}
```

---

## 工具执行流程

```
用户请求
   │
   ▼
┌──────────────────┐
│ 1. 获取工具定义   │
│    ToolService   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. 检查启用状态   │
│    is_active?    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. 组装 JS 脚本   │
│ wrap_javascript_ │
│    _code()       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. 执行工具       │
│ quickjs_tool 执行 │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. 返回结果       │
│   JSON 解析      │
└──────────────────┘
```

---

## 工具系统 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/tools` | GET | 获取工具列表 |
| `/api/tools/{id}` | GET | 获取单个工具 |
| `/api/tools` | POST | 创建工具 |
| `/api/tools` | PUT | 更新工具 |
| `/api/tools/{id}` | DELETE | 删除工具 |
| `/api/tools/import` | POST | 批量导入工具 |
| `/api/tools/export` | GET | 导出所有工具 |
| `/api/tools/inheritable` | GET | 获取可继承工具 |
| `/api/tools/active` | PUT | 切换启用状态 |
| `/api/tools/execute` | POST | 同步执行工具 |
| `/api/tools/execute/stream` | POST | 流式执行工具 |

---

# 技能系统

---

## 技能系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    技能数据目录                           │
│              data/skills/{skill}/                       │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────▼───────┐
│  SKILL.md (YAML + Markdown) │
└───────────┬─────────────┘
            │
┌───────────▼───────────┐
│   SkillLoader         │
│   - 加载技能文件       │
│   - 解析 YAML frontmatter │
└───────────┬───────────┘
            │
┌───────────▼───────────┐
│   SkillExecutor       │
│   - 参数替换           │
│   - 内容渲染           │
└───────────┬───────────┘
            │
┌───────────▼───────────┐
│   SkillTool (LLM)     │
│   - LLM 自动调用       │
│   - 插入对话上下文     │
└───────────────────────┘
```

---

## 当前可用技能

| 技能名称 | 描述 | 适用场景 |
|----------|------|----------|
| **my-skill** | 示例技能模板 | 学习技能创建 |
| **order** | 订单管理技能 | 订单处理、进度跟踪 |
| **pdf** | PDF 处理技能 | PDF 提取、转换、处理 |
| **workstation** | 工作站技能 | 工作站信息查询 |
| **xlsx** | Excel 技能 | Excel 文件处理 |

---

## 技能文件格式

```markdown
---
name: pdf
description: PDF 处理技能
license: Proprietary
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations...

## Quick Start

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations
...
```

**YAML Frontmatter 字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 技能名称 |
| description | string | 技能描述 (LLM 理解) |
| license | string | 许可证 (可选) |
| argument_hint | string | 参数提示 (可选) |
| when_to_use | string | 使用场景 (可选) |

---

## 技能调用流程

```
用户: "帮我处理一个 PDF 文件"

   │
   ▼
┌──────────────────┐
│ LLM 分析意图       │
│ 检测到需要 skill 工具 │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 调用 skill 工具    │
│ {skill_name: "pdf"} │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SkillExecutor    │
│ 加载 pdf 技能内容   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 插入对话上下文     │
│ 提供 PDF 操作指南  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM 基于技能内容   │
│ 生成详细回复       │
└──────────────────┘
```

---

## 技能高级特性

### 参数占位符

技能内容支持 `{param_name}` 格式的占位符：

```markdown
---
name: custom
description: 自定义技能
---

执行操作: {action}
目标: {target}
```

调用时传入参数：
```json
{
  "skill_name": "custom",
  "args": {
    "action": "分析数据",
    "target": "销售报表"
  }
}
```

### 工具授权

技能可指定允许使用的工具列表：
```yaml
---
name: pdf
allowed_tools:
  - read_file
  - bash
  - quickjs
---
```

---

---
# MCP Server 系统

---

## MCP Server 介绍

MCP (Model Context Protocol) Server 是一类特殊的 LLM 工具服务器，通过统一的协议标准提供各种能力。WIMI CHAT v4.0 已集成 MCP Server 支持，可轻松接入各种第三方工具。

MCP Server 通过标准协议对外提供工具列表，系统自动注册为可用工具，与内置工具和动态工具共同构成完整的工具体系。

---

## MCP Server 配置

配置文件位于 `backend/mcp_servers.json`：

```json
{
  "mcpServers": {
    "my_sqlite_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "sqlite:///data/app.db"
      }
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.4"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    }
  }
}
```

---

## 支持的传输模式

| 传输模式 | 说明 | 使用场景 |
|----------|------|----------|
| **stdio** | 通过标准输入输出与进程通信 | 本地命令行工具 (uvx/npx) |
| **http** | 通过 HTTP 协议通信 | 远程 MCP 服务器 |

---

## 当前集成的 MCP 工具

| 服务器名称 | 功能 | 依赖 |
|------------|------|------|
| **my_sqlite_db** | SQLite 数据库查询 | mcp-alchemy |
| **fetch** | 网络请求 | mcp-server-fetch |
| **context7** | 文档查询 | @upstash/context7-mcp |
| **tavily-mcp** | 搜索和提取 | tavily-mcp |

---

## 技术实现

### MCPClient

异步 MCP 客户端，支持：
- Stdio 传输（本地进程）
- Streamable HTTP 传输（远程服务）
- 懒连接管理（按需连接）
- 自动重连机制

### MCPToolAdapter

MCP 工具适配器，将 MCP 服务器的工具注册到工具注册表：

```python
# 自动发现 MCP 服务器的工具
tools_meta = register_mcp_tools(tool_registry, client, namespace="tavily-mcp")

# 注册的工具示例
# - tavily-mcp_tavily_search: 搜索网络信息
# - tavily-mcp_tavily_extract: 提取网页内容
```

---

## MCP Server 架构

```
┌─────────────────────────────────────────────────────────┐
│              WIMI CHAT MCP 集成层                        │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │   MCP Server 配置      │
        │  mcp_servers.json     │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │   MCP Client Wrapper  │
        │   - Stdio Transport   │
        │   - HTTP Transport    │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │  MCP Protocol Adapter │
        │  - list_tools         │
        │  - call_tool          │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │  工具注册中心          │
        │  (如: tavily_search)  │
        └───────────────────────┘
```

---

## 工具系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    工具注册中心                           │
│              src/tools/registry.py                       │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴───────┬───────┐
        │               │       │
┌───────▼───────┐ ┌────▼──────┐ ┌───────▼───────┐
│ 内置工具池      │ │ 动态工具池 │ │ MCP 工具池     │
│ (builtins/)   │ │ (数据库)   │ │ (MCP Servers) │
└───────────────┘ └───────────┘ └───────────────┘
        │               │       │
        └───────┬───────┘       │
                │               │
        ┌───────▼───────┐       │
│   LLM 调用工具时       │       │
│   注册中心执行对应工具   │       │
└───────────────────────┘       │
                                │
                    ┌───────────▼───────────┐
                    │  统一工具执行接口        │
                    └───────────────────────┘
```

---

## 目录

1. [产品概述](#产品概述)
2. [核心架构](#核心架构)
3. [后端能力](#后端能力)
4. [前端界面](#前端界面)
5. [工具系统](#工具系统)
6. [技能系统](#技能系统)
7. [MCP Server 系统](#mcp-server-系统)
8. [技术特点](#技术特点)
9. [应用场景](#应用场景)

---

# 技术特点

---

## 架构优势

### 1. 分层架构

```
DAO → Service → API
```

- **DAO 层**: 数据访问对象
- **Service 层**: 业务逻辑处理
- **API 层**: HTTP 接口暴露

### 2. 依赖注入

```python
# 使用 injector 管理服务生命周期
 injector = Injector([
    DatabaseModule(),
    ToolsModule()
])
```

### 3. 模块化设计

- 工具系统独立可扩展
- 技能系统与核心分离
- LLM 适配器统一接口

---

## SSE 流式通信

### 前端 SSE 客户端

```typescript
class StreamRequest {
  async stream(url: string, eventHandler: EventHandlers) {
    const response = await fetch(url, { ... });
    const reader = response.body.getReader();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = new TextDecoder().decode(value);
      // 解析 SSE 事件
      // content, thinking, tool_call, tool_result, done, error
    }
  }
}
```

### SSE 事件类型

| 事件类型 | 数据格式 | 说明 |
|----------|----------|------|
| `content` | string | 文本内容块 |
| `thinking` | object | 思考过程 |
| `tool_call` | object | 工具调用信息 |
| `tool_result` | object | 工具执行结果 |
| `done` | null | 流结束 |
| `error` | object | 错误信息 |

---

## 配置管理

### 多层级配置

```
config.yaml
    │
    ├── config.dev.yaml      (环境配置)
    ├── config.prod.yaml     (生产配置)
    └── config.local.yaml    (本地覆盖)
```

### 支持环境变量

```yaml
openai:
  api_url: ${API_URL::https://api.openai.com/v1}
  api_key: ${API_KEY::sk-xxx}
  model: ${API_MODEL::gpt-4}
```

---

# 应用场景

---

## 典型应用场景

| 场景 | 描述 | 使用功能 |
|------|------|----------|
| **文档处理** | PDF/Excel 文档提取和转换 | PDF 技能 + 读文件工具 |
| **数据查询** | 从数据库查询数据 | 自定义 SQL 工具 |
| **系统管理** | 执行系统命令 | Bash 工具 |
| **智能助手** | 日常对话和知识问答 | LLM 基础能力 |
| ** workflow** | 自定义业务流程 | 动态工具 + 技能 |
| **Web API** | 调用外部 API | HTTP 工具 |

---

## 开发者场景

### 快速开发自定义工具

```javascript
// 自定义 JavaScript 工具
{
  name: "calculate_profit",
  description: "计算净利润",
  code: `
    const revenue = params.revenue || 0;
    const cost = params.cost || 0;
    return { result: revenue - cost };
  `
}
```

### 创建领域技能

```markdown
---
name: sales
description: 销售技能
---

# 销售流程指南

## 1. 客户跟进
...

## 2. 需求分析
...

## 3. 方案报价
...
```

---

## 运维部署

### Docker 部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "src", "--web", "--port", "8000"]
```

### 环境变量配置

```bash
# .env
LLM_PROVIDER=qwen
API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_KEY=sk-xxx
API_MODEL=qwen3-8b
TAVILY_API_KEY=tvly-xxx  # MCP Tavily 工具需要
```

---

# 总结

---

## 核心价值

| 维度 | 说明 |
|------|------|
| **双模式支持** | CLI + Web 满足不同使用场景 |
| **流式响应** | SSE 实时交互体验 |
| **可扩展工具** | 内置 + 动态工具 + MCP工具轻松扩展 |
| **技能复用** | 预定义技能快速复用 |
| **技术先进** | FastAPI + Vue 3 现代技术栈 |
| **MCP集成** | 支持 Model Context Protocol 标准 |

---

## 未来规划

- [ ] 多用户认证系统
- [ ] 对话历史云端同步
- [ ] 支持更多 LLM 提供商

---

## 联系我们

**WIMI CHAT 开发团队**

- 项目文档: `docs/`
- 后端文档: `backend-master/backend/CLAUDE.md`
- 前端文档: `frontend-master/frontend_chat/CLAUDE.md`

---

## Q&A

感谢聆听！
