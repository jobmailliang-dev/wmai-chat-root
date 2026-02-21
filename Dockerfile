# LLM CLI V4 Dockerfile

# 阶段 1: 构建前端
FROM node:20-slim AS frontend-builder

# 安装 pnpm
RUN npm install -g pnpm@9

# 设置工作目录
WORKDIR /app

# 复制 workspace 配置和前端代码
COPY frontend-master/package.json /app/
COPY frontend-master/pnpm-workspace.yaml /app/
COPY frontend-master/frontend_chat /app/frontend_chat
COPY frontend-master/frontend_settings /app/frontend_settings
COPY frontend-master/packages /app/packages

# 安装依赖并构建
RUN pnpm install --frozen-lockfile
RUN pnpm --filter wimi-chat-frontend build

# 阶段 2: Python 后端
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STATIC_DIR=/app/static

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 依赖文件
COPY backend/requirements.txt /app/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制后端代码
COPY backend/src /app/src
COPY backend/data /app/data
COPY backend/config.yaml /app/config.yaml

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/frontend_chat/dist /app/static

# 创建必要的目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动应用
CMD ["python", "-m", "src", "--web", "--env", "prod"]
