@echo off
set PORT=3002

echo [Mock] 检查端口 %PORT% 是否被占用...

:: 查找占用端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    set PID=%%a
    echo [Mock] 发现端口 %PORT% 被进程 %%a 占用，正在关闭...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul

echo [Mock] 启动 Mock 服务器...
start /B node mock-server.js

echo [Mock] 启动 Vite 开发服务器...
npm run dev:mock
