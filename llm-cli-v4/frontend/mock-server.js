// Mock SSE 服务器
// 使用方式: node mock-server.js

import http from 'http'
import url from 'url'

const PORT = 3002

const sendSSE = (res, event, data) => {
  res.write(`event: ${event}\n`)
  res.write(`data: ${data}\n\n`)
}

const routes = {
  '/api/chat/stream': (req, res) => {
    const query = url.parse(req.url, true).query
    const message = query.message || ''
    console.log(`[Mock] 收到消息: ${message}`)

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive', // 虽然是 keep-alive，但 res.end() 会结束当前响应块
      'Access-Control-Allow-Origin': '*'
    })

    // 模拟流式响应
    setTimeout(() => sendSSE(res, 'content', `你好！我收到了: "${message}"`), 100)
    setTimeout(() => sendSSE(res, 'content', '这是一个模拟的 SSE 流式响应'), 300)
    setTimeout(() => sendSSE(res, 'content', 'MSW 拦截正常工作'), 500)
    
    // 关键修复点：
    setTimeout(() => {
      sendSSE(res, 'done', '') // 发送业务上的结束标识（可选）
      res.end()                // 真正关闭 HTTP 连接，触发前端 reader.read() 的 done: true
      console.log(`[Mock] 响应已结束`)
    }, 700)
  },
  '/api/health': (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }))
  },

  'api/tools': (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(JSON.stringify([
      { name: 'bash', description: 'Execute bash commands' },
      { name: 'calculator', description: 'Perform calculations' },
      { name: 'datetime', description: 'Get current date and time' },
      { name: 'read_file', description: 'Read file contents' },
      { name: 'skill', description: 'Call a skill' }
    ]))
  }
}

const server = http.createServer((req, res) => {
  const pathname = url.parse(req.url, true).pathname

  // CORS 预检请求
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    })
    res.end()
    return
  }

  const handler = routes[pathname]
  if (handler) {
    handler(req, res)
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*' })
    res.end('Not Found')
  }
})

server.listen(PORT, () => {
  console.log(`[Mock Server] 运行在 http://localhost:${PORT}`)
  console.log(`[Mock Server] SSE 端点: http://localhost:${PORT}/api/chat/stream?message=你的消息`)
  console.log(`[Mock Server] 健康检查: http://localhost:${PORT}/api/health`)
  console.log(`[Mock Server] 工具列表: http://localhost:${PORT}/api/tools`)
})
