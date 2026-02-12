// Mock SSE 服务器
// 使用方式: node mock-server.js

import http from 'http'
import { parse } from 'url'
import { parse as parseQueryString } from 'querystring'

const PORT = 3002

// 模拟数据存储（内存中）
const conversations = new Map()
const messages = new Map()

// 生成唯一ID
const generateId = () => {
  const now = Date.now().toString(36)
  const rand = Math.random().toString(36).substring(2, 8)
  return `conv_${now}_${rand}`
}

const sendSSE = (res, event, data) => {
  res.write(`event: ${event}\n`)
  res.write(`data: ${data}\n\n`)
}

const routes = {
  '/api/chat/stream': (req, res) => {
    const query = parseQueryString(parse(req.url).query)
    const message = query.message || ''
    console.log(`[Mock] 收到消息: ${message}`)

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    })

    // 模拟流式响应
    setTimeout(() => sendSSE(res, 'content', `你好！我收到了: "${message}"`), 100)
    setTimeout(() => sendSSE(res, 'content', '这是一个模拟的 SSE 流式响应'), 300)
    setTimeout(() => sendSSE(res, 'content', 'MSW 拦截正常工作'), 500)

    setTimeout(() => {
      sendSSE(res, 'done', '')
      res.end()
      console.log(`[Mock] 响应已结束`)
    }, 700)
  },

  '/api/health': (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }))
  },

  '/api/tools': (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(JSON.stringify([
      { name: 'bash', description: 'Execute bash commands' },
      { name: 'calculator', description: 'Perform calculations' },
      { name: 'datetime', description: 'Get current date and time' },
      { name: 'read_file', description: 'Read file contents' },
      { name: 'skill', description: 'Call a skill' }
    ]))
  },

  '/api/conversations': (req, res) => {
    const parsedUrl = parse(req.url, true)
    const query = parsedUrl.query

    // GET: 获取对话列表
    if (req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
      const list = Array.from(conversations.values())
      list.sort((a, b) => b.updateTime - a.updateTime)
      res.end(JSON.stringify(list))
      return
    }

    // POST: 创建对话
    if (req.method === 'POST') {
      const title = query.title || '新对话'
      const now = Date.now()
      const id = generateId()

      const conversation = {
        id,
        title,
        preview: '',
        createTime: now,
        updateTime: now,
        messageCount: 0
      }

      conversations.set(id, conversation)
      messages.set(id, [])

      console.log(`[Mock] 创建对话: ${id} - ${title}`)
      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
      res.end(JSON.stringify(conversation))
      return
    }

    // DELETE: 删除对话
    if (req.method === 'DELETE') {
      const id = query.id
      if (!id) {
        res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
        res.end(JSON.stringify({ error: '缺少 id 参数' }))
        return
      }

      if (conversations.has(id)) {
        conversations.delete(id)
        messages.delete(id)
        console.log(`[Mock] 删除对话: ${id}`)
      }

      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
      res.end(JSON.stringify({ success: true }))
      return
    }

    // PATCH: 更新对话
    if (req.method === 'PATCH') {
      const id = query.id
      if (!id) {
        res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
        res.end(JSON.stringify({ error: '缺少 id 参数' }))
        return
      }

      const conv = conversations.get(id)
      if (!conv) {
        res.writeHead(404, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
        res.end(JSON.stringify({ error: '对话不存在' }))
        return
      }

      if (query.title) conv.title = query.title
      if (query.preview !== undefined) conv.preview = query.preview
      if (query.messageCount !== undefined) conv.messageCount = parseInt(query.messageCount)
      conv.updateTime = Date.now()

      console.log(`[Mock] 更新对话: ${id}`)
      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
      res.end(JSON.stringify(conv))
      return
    }

    res.writeHead(405, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(JSON.stringify({ error: 'Method not allowed' }))
  },

  '/api/conversations/messages': (req, res) => {
    const query = parseQueryString(parse(req.url).query)
    const conversationId = query.conversationId || query.id

    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })

    if (!conversationId) {
      res.end(JSON.stringify({ conversationId: '', messages: [] }))
      return
    }

    const conversationMessages = messages.get(conversationId) || []
    res.end(JSON.stringify({
      conversationId,
      messages: conversationMessages
    }))
  }
}

const server = http.createServer((req, res) => {
  const pathname = parse(req.url, true).pathname

  // CORS 预检请求
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
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
  console.log(`[Mock Server] 对话列表: http://localhost:${PORT}/api/conversations (GET)`)
  console.log(`[Mock Server] 创建对话: POST /api/conversations?title=标题`)
  console.log(`[Mock Server] 删除对话: DELETE /api/conversations?id=xxx`)
  console.log(`[Mock Server] 更新对话: PATCH /api/conversations?id=xxx&title=新标题`)
  console.log(`[Mock Server] 获取消息: GET /api/conversations/messages?conversationId=xxx`)
})
