# LLM CLI V4

LLM CLI V4 是一个支持 CLI 和 Web 双模式的 AI 对话应用，通过集成 OpenAI 兼容 API 实现大语言模型交互。该项目支持工具调用、技能系统、SSE 流式响应，为 Claude 等 LLM 提供结构化的工具执行能力。

## 功能特性

- **Web 模式**: 基于 FastAPI 的 Web 服务，支持 SSE 流式响应
- **CLI 模式**: 交互式命令行界面
- **工具系统**: 可扩展的工具注册和执行框架（内置 Bash、计算器、日期时间、文件读取等工具）
- **技能系统**: 动态加载和执行技能内容，支持占位符替换
- **多 LLM 支持**: 支持 OpenAI、Qwen 等兼容 API
- **环境配置分离**: 支持 dev/prod/local 多环境配置

## 技术栈

| 技术 | 版本要求 |
|------|----------|
| Python | >= 3.11.14 |
| FastAPI | >= 0.109.0 |
| Uvicorn | >= 0.27.0 |
| OpenAI Python SDK | >= 1.0.0 |

## 文件结构

```
llm-cli-demo-v4/
├── backend/                  # 后端服务
│   ├── src/                 # 源代码
│   │   ├── api/             # API 路由层
│   │   ├── core/            # 核心业务逻辑
│   │   ├── modules/         # 业务模块
│   │   ├── tools/           # 工具系统
│   │   ├── skills/          # 技能系统
│   │   ├── adapters/        # LLM 适配器
│   │   ├── config/          # 配置管理
│   │   ├── utils/           # 通用工具
│   │   └── web/             # Web 中间件
│   ├── data/                # 技能数据
│   │   └── skills/          # 技能目录
│   ├── static/              # 前端构建产物
│   ├── requirements.txt     # Python 依赖
│   └── config.yaml          # 基础配置
├── frontend/                # Vue.js 前端
├── docs/                    # 项目文档
├── Dockerfile               # Docker 构建文件
└── README.md                # 项目说明
```

## 快速开始

### 前置要求

- Python >= 3.11.14
- Docker (可选，用于容器化部署)

### 本地开发

#### 1. 克隆项目

```bash
git clone <repository-url>
cd llm-cli-demo-v4
```

#### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 配置环境

复制 `config.yaml` 并根据需要创建环境配置文件：

```bash
# 开发环境配置（可选）
cp config.yaml config.dev.yaml
# 编辑 config.dev.yaml 添加开发环境的 API 密钥等配置

# 本地覆盖配置（可选）
cp config.yaml config.local.yaml
# 编辑 config.local.yaml 添加本地覆盖配置
```

#### 5. 启动服务

```bash
# Web 模式（默认端口 8000）
python -m src --web

# 指定环境
python -m src --web --env dev

# CLI 模式
python -m src --cli
```

访问 http://localhost:8000 查看 Web 界面，API 文档位于 http://localhost:8000/docs

### Docker 部署

#### 1. 构建镜像

```bash
docker build -t llm-cli-v4 .
```

#### 2. 运行容器

```bash
# 使用默认配置
docker run -d -p 8000:8000 --name llm-cli-v4 llm-cli-v4

# 挂载配置文件
docker run -d -p 8000:8000 \
  -v /path/to/config.yaml:/app/config.yaml \
  --name llm-cli-v4 llm-cli-v4

# 使用环境变量
docker run -d -p 8000:8000 \
  -e APP_ENV=prod \
  -e PYTHONUNBUFFERED=1 \
  --name llm-cli-v4 llm-cli-v4
```

#### 3. Docker Compose（推荐）

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  llm-cli:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - APP_ENV=prod
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

启动服务：

```bash
docker-compose up -d
```

## 配置说明

### 配置文件优先级

配置加载顺序（后者覆盖前者）：
1. `config.yaml` - 基础配置（共享，非敏感）
2. `config.{env}.yaml` - 环境配置（dev/prod/local）
3. `config.local.yaml` - 本地覆盖

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| APP_ENV | 运行环境 | dev |

### 配置示例

```yaml
# config.yaml（基础配置）
llm:
  provider: qwen

qwen:
  api_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "${QWEN_API_KEY}"
  model: "qwen3-14b"

server:
  host: "0.0.0.0"
  port: 8000

tools:
  allowed_tools:
    - bash
    - calculator
    - datetime
    - read_file
    - skill
```

```yaml
# config.dev.yaml（开发环境）
qwen:
  api_key: "dev-api-key"

server:
  port: 8000
```

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 界面 |
| `/docs` | GET | Swagger API 文档 |
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 同步聊天 |
| `/api/chat/stream` | GET | SSE 流式聊天 |
| `/api/tools` | GET | 工具列表 |
| `/api/conversations` | GET | 对话列表 |

## 技能系统

技能是预定义的上下文内容，支持占位符替换：

- 技能文件格式：`SKILL.md`（支持 YAML frontmatter）
- 技能目录：`data/skills/{skill_name}/`
- 技能调用：使用 `skill` 工具动态加载

## 许可证

MIT License
