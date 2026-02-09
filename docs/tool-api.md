# 工具管理接口对接文档

## 概述

本文档描述了工具管理模块的前后端接口规范，供前端开发与后端 API 对接使用。

**API 基础路径**: `/api/tools`

**响应包装格式**:
```typescript
interface ApiResponse<T> {
  success: boolean;   // 操作是否成功
  data: T;          // 响应数据
  message?: string; // 提示信息
  error?: string;   // 错误信息
}
```

---

## 接口列表

### 1. 获取工具列表

**接口**: `GET /api/tools`

**说明**: 获取所有工具列表

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "bash",
      "description": "执行 Bash 命令",
      "is_active": true,
      "parameters": [
        {
          "name": "command",
          "description": "要执行的命令",
          "type": "string",
          "required": true
        }
      ],
      "code": "...",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:00:00Z"
    }
  ]
}
```

---

### 2. 获取单个工具

**接口**: `GET /api/tools?id={id}`

**说明**: 根据 ID 获取单个工具详情（与列表接口共用，通过 id 参数区分）

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 工具 ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "bash",
    "description": "执行 Bash 命令",
    "is_active": true,
    "parameters": [...],
    "code": "...",
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  }
}
```

**错误响应** (工具不存在):
```json
{
  "success": false,
  "error": "Tool not found"
}
```
**HTTP 状态码**: 404

---

### 3. 创建工具

**接口**: `POST /api/tools`

**说明**: 创建新工具

**请求体**:
```json
{
  "name": "my_tool",
  "description": "自定义工具描述",
  "is_active": true,
  "parameters": [
    {
      "name": "param1",
      "description": "参数描述",
      "type": "string",
      "required": true,
      "default": "default_value"
    }
  ],
  "code": "tool code here"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Tool created",
  "data": {
    "id": 2,
    "name": "my_tool",
    "description": "自定义工具描述",
    "is_active": true,
    "parameters": [...],
    "code": "...",
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "工具名称不能为空"
}
```
**HTTP 状态码**: 400

---

### 4. 更新工具

**接口**: `PUT /api/tools?id={id}`

**说明**: 更新指定工具的信息

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 工具 ID |

**请求体**:
```json
{
  "name": "updated_tool",
  "description": "更新后的描述",
  "is_active": false,
  "parameters": [...]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Tool updated",
  "data": {
    "id": 1,
    "name": "updated_tool",
    "description": "更新后的描述",
    "is_active": false,
    "parameters": [...],
    "code": "...",
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
}
```

---

### 5. 删除工具

**接口**: `DELETE /api/tools?id={id}`

**说明**: 删除指定工具

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 工具 ID |

**响应示例**:
```json
{
  "success": true,
  "message": "Tool deleted"
}
```

---

### 6. 批量导入工具

**接口**: `POST /api/tools/import`

**说明**: 批量导入工具配置

**请求体**:
```json
{
  "tools": [
    {
      "name": "tool1",
      "description": "工具1",
      "is_active": true,
      "parameters": [...],
      "code": "..."
    },
    {
      "name": "tool2",
      "description": "工具2",
      "is_active": true,
      "parameters": [...],
      "code": "..."
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "2 tools imported",
  "data": [
    {
      "id": 3,
      "name": "tool1",
      "...": "..."
    },
    {
      "id": 4,
      "name": "tool2",
      "...": "..."
    }
  ]
}
```

---

### 7. 导出工具

**接口**: `GET /api/tools/export`

**说明**: 导出所有工具为 JSON 数据

**响应示例**:
```json
{
  "success": true,
  "data": [...]
}
```

---

### 8. 获取可继承工具列表

**接口**: `GET /api/tools/inheritable`

**说明**: 获取所有已启用的工具列表（下拉选择用）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "bash",
      "description": "执行 Bash 命令"
    },
    {
      "id": 2,
      "name": "calculator",
      "description": "数学计算"
    }
  ]
}
```

---

### 9. 切换工具启用状态

**接口**: `PUT /api/tools/active?id={id}`

**说明**: 切换工具的启用/停用状态

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 工具 ID |

**请求体**:
```json
{
  "is_active": false
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "已停用",
  "data": {
    "id": 1,
    "name": "bash",
    "is_active": false,
    "...": "..."
  }
}
```

---

### 10. 执行工具

**接口**: `POST /api/tools/execute?id={id}`

**说明**: 执行指定工具

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 工具 ID |

**请求体**:
```json
{
  "params": {
    "command": "ls -la"
  }
}
```

**响应示例** (成功):
```json
{
  "success": true,
  "data": {
    "result": "total 16\ndrwxr-xr-x  5 user  staff  160 Feb  9 10:00 .\n...",
    "execution_time": "0.023s"
  }
}
```

**响应示例** (失败):
```json
{
  "success": false,
  "error": "Command execution failed",
  "execution_time": "0.001s"
}
```

---

## 数据结构

### ToolConfig 工具配置

```typescript
interface ToolConfig {
  id?: number;              // 工具 ID (创建后返回)
  name: string;            // 工具名称
  description: string;     // 工具描述
  is_active: boolean;      // 是否启用
  parameters: ToolParameter[]; // 参数定义列表
  inherit_from?: string;   // 继承自的工具名称
  code: string;            // 工具代码
  created_at?: string;    // 创建时间
  updated_at?: string;    // 更新时间
}
```

### ToolParameter 工具参数

```typescript
interface ToolParameter {
  name: string;           // 参数名称
  description: string;    // 参数描述
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;      // 是否必填
  default?: any;          // 默认值
  enum?: string[];       // 可选值枚举
}
```

### ToolExecuteRequest 工具执行请求

```typescript
interface ToolExecuteRequest {
  params: Record<string, any>; // 参数键值对
}
```

### ToolExecuteResponse 工具执行响应

```typescript
interface ToolExecuteResponse {
  success: boolean;       // 执行是否成功
  data?: any;            // 执行结果数据
  error?: string;         // 错误信息
  execution_time?: string; // 执行耗时
}
```

---

## 错误码说明

| HTTP 状态码 | success | error 说明 |
|-------------|---------|------------|
| 200 | true | - |
| 400 | false | 请求参数错误 |
| 404 | false | 工具不存在 |
| 500 | false | 服务器内部错误 |

---

## 前端调用示例

```typescript
import request from './request';

const API_BASE = '/api/tools';

// 获取工具列表
const getTools = async () => {
  const response = await request.get(`${API_BASE}`);
  return response.data.data;
};

// 获取单个工具
const getTool = async (id) => {
  const response = await request.get(`${API_BASE}?id=${id}`);
  return response.data.data;
};

// 创建工具
const createTool = async (tool) => {
  const response = await request.post(API_BASE, tool);
  return response.data;
};

// 更新工具
const updateTool = async (id, tool) => {
  const response = await request.put(`${API_BASE}?id=${id}`, tool);
  return response.data;
};

// 删除工具
const deleteTool = async (id) => {
  const response = await request.delete(`${API_BASE}?id=${id}`);
  return response.data;
};

// 切换启用状态
const toggleActive = async (id, isActive) => {
  const response = await request.put(`${API_BASE}/active?id=${id}`, { is_active: isActive });
  return response.data;
};

// 执行工具
const executeTool = async (id, params) => {
  const response = await request.post(`${API_BASE}/execute?id=${id}`, { params });
  return response.data;
};
```

---

## 注意事项

1. **查询参数规则**: 单资源操作（查询、更新、删除、执行）统一使用查询参数 `?id={id}`
2. **时间格式**: 所有时间字段使用 ISO 8601 格式 (`YYYY-MM-DDTHH:mm:ssZ`)
3. **工具分类**:
   - **内置工具**: 系统预置的工具（如 bash、calculator），不可删除
   - **自定义工具**: 用户创建的工具，可增删改
4. **执行权限**: 只有 `is_active=true` 的工具才能被执行
