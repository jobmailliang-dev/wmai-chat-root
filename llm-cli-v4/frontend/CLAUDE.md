# Frontend CLAUDE.md

本文档为 Vue 3 前端提供开发指导和规范。

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 调用封装
│   │   ├── conversation.ts  # 对话相关 API
│   │   └── ...
│   ├── components/       # UI 组件
│   │   ├── ChatWindow.vue   # 聊天窗口
│   │   ├── Sidebar.vue     # 侧边栏
│   │   ├── ConfirmDialog.vue # 确认对话框
│   │   └── RenameDialog.vue  # 重命名对话框
│   ├── hooks/            # 组合式函数
│   │   ├── useChat.ts      # 聊天逻辑
│   │   └── useConversation.ts # 对话管理
│   ├── types/            # 类型定义
│   │   └── conversation.ts
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口文件
├── index.html
├── vite.config.ts
└── package.json
```

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 框架 | Vue 3 + TypeScript |
| 构建工具 | Vite 5.x |
| 样式 | 原生 CSS + CSS Variables |

## 开发规范

### 组件命名

- 使用 PascalCase (如 `ChatWindow.vue`)
- 组件文件即组件名

### TypeScript 规范

- **Vue 3**：使用 Composition API + `<script setup>`
- **类型安全**：严格模式启用
- **导入排序**：Vue API → 第三方 → 本地导入

### Dialog 组件规范

所有 Dialog/Modal 弹窗组件统一使用以下样式规范：

#### 模板结构
```vue
<Teleport to="body">
  <Transition name="dialog">
    <div v-if="visible" class="dialog-overlay" @click="handleCancel">
      <div class="dialog-container" @click.stop>
        <!-- 标题栏 -->
        <div class="dialog-header">
          <h3 class="dialog-title">{{ title }}</h3>
          <button class="close-btn" @click="handleCancel">×</button>
        </div>
        <!-- 内容区/输入框 -->
        <div class="dialog-content">...</div>
        <!-- 操作栏 -->
        <div class="dialog-actions">...</div>
      </div>
    </div>
  </Transition>
</Teleport>
```

#### 样式变量 (浅色主题)
```css
.dialog-overlay {
  --background-white: #ffffff;
  --text-primary: #1f1f1f;
  --text-secondary: rgba(0, 0, 0, 0.7);
  --text-tertiary: #8c8c8c;
  --fill-gray-light: #f5f5f5;
  --fill-gray-hover: #e8e8e8;
  --border-light: #e5e5e5;
  --icon-tertiary: #8c8c8c;
  --Button-primary-blue: #007aff;
  --Button-primary-red: #ff4d4f;
}
```

#### 关键样式规格
| 属性 | 值 | 说明 |
|------|-----|------|
| 容器宽度 | 360-400px | 标准宽度 |
| 圆角 | 20px | 大圆角 |
| 阴影 | 0 24px 48px rgba(0,0,0,0.15) | 柔和阴影 |
| 遮罩 | rgba(0,0,0,0.4) + blur(4px) | 半透明磨砂 |
| 按钮高度 | 36px | 固定高度 |
| 按钮圆角 | 8px | 小圆角 |
| 过渡动画 | cubic-bezier(0.34,1.56,0.64,1) | 弹性效果 |

#### 按钮类型
- **确认/主要按钮**：蓝色背景 + 白色文字
- **取消/次要按钮**：透明背景 + 边框
- **删除/危险按钮**：红色背景 + 白色文字

#### 现有组件
- `ConfirmDialog.vue` - 确认对话框
- `RenameDialog.vue` - 重命名对话框

## 状态管理

### useConversation (对话管理)

```typescript
const {
  conversations,      // 对话列表 (computed)
  currentConversationId, // 当前对话 ID (ref)
  isLoading,          // 加载状态 (computed)
  loadConversations,  // 加载对话列表
  createConversation, // 创建对话
  selectConversation, // 选择对话
  deleteConversation, // 删除对话
  updateConversation, // 更新对话
  resetCurrentConversation, // 重置当前对话
} = useConversation();
```

### useChat (聊天逻辑)

```typescript
const {
  messages,     // 消息列表
  state,        // 聊天状态
  streamMessage, // 发送消息(流式)
  clearMessages, // 清空消息
} = useChat(baseUrl);
```

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/conversations` | GET | 获取对话列表 |
| `/api/conversations` | POST | 创建对话 |
| `/api/conversations` | DELETE | 删除对话 |
| `/api/conversations` | PATCH | 更新对话 |
| `/api/conversations/messages` | GET | 获取对话消息 |

## 运行命令

```bash
# 开发模式 (端口 3000)
npm run dev

# 使用 Mock API
npm run dev:mock

# 构建生产版本
npm run build
```

## 注意事项

1. **Vue Teleport**：弹窗组件必须使用 `<Teleport to="body">`
2. **点击外部关闭**：弹窗需支持点击遮罩层关闭
3. **ref vs computed**：状态共享时返回 ref 而非 computed
4. **API 代理**：开发环境通过 Vite 代理转发 API 请求
