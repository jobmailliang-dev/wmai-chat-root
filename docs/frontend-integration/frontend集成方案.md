# 集成改造计划：frontend_next 作为组件库嵌入 frontend_chat

## 目标

将 `frontend_next` 改造为可独立运行的组件库，通过设置弹框形式嵌入 `frontend_chat` 应用。

## 目录结构规划

```
open-agent/
├── frontend_chat/                    # 主应用
│   ├── src/
│   │   ├── components/
│   │   │   └── SettingsDialog.vue    # [新增] 设置弹框
│   │   ├── router/                   # [新增]
│   │   │   └── index.ts
│   │   ├── stores/                   # [新增]
│   │   │   └── settings.ts
│   │   ├── views/                    # [新增] 嵌入的管理页面
│   │   │   ├── AdminHome.vue
│   │   │   ├── AdminWorkbench.vue
│   │   │   └── AdminTools.vue
│   │   ├── App.vue                   # [修改] 添加弹框
│   │   └── main.ts                   # [修改] 添加路由/Pinia
│   ├── package.json                  # [修改] 添加依赖
│   └── vite.config.ts               # [修改] 配置路径别名
│
├── frontend_next/                    # 组件库源
│   ├── src/
│   │   ├── components/              # 可复用组件（保留）
│   │   │   ├── MainLayout.vue
│   │   │   ├── ToolCard.vue
│   │   │   └── ToolParamForm.vue
│   │   ├── views/                    # 页面组件（保留）
│   │   ├── router/                   # 路由配置（保留）
│   │   ├── stores/                   # 状态管理（保留）
│   │   ├── embed/                    # [新增] 嵌入式入口
│   │   │   ├── index.ts              # 导出所有可嵌入组件
│   │   │   ├── useAdminRouter.ts     # 嵌入式路由 hook
│   │   │   └── AdminLayout.vue       # 嵌入式 Layout（简化版）
│   │   ├── App.vue                   # [修改] 添加 embed 导出
│   │   └── main.ts                   # [修改] 支持 embed 模式
│   └── package.json                  # [修改] 导出配置
│
└── packages/
    └── shared-types/                 # [新增] 共享类型
        ├── index.ts
        └── tool.ts
```

## 详细执行步骤

### 步骤 1：创建共享类型包

**文件**: `packages/shared-types/index.ts`

```typescript
// 工具配置类型
export interface ToolConfig {
  id?: number;
  name: string;
  description: string;
  is_active: boolean;
  parameters: ToolParameter[];
  inherit_from?: string;
  code: string;
  created_at?: string;
  updated_at?: string;
}

export interface ToolParameter {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  default?: any;
  enum?: string[];
}

// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  avatar_url?: string;
}
```

**预期结果**:
- 创建 `packages/shared-types/` 目录
- 创建基础类型定义文件
- frontend_chat 和 frontend_next 都可以引用此类型

---

### 步骤 2：改造 frontend_next - 添加嵌入式入口

**文件**: `frontend_next/src/embed/index.ts`

```typescript
// 嵌入式入口 - 导出所有可嵌入组件

export { default as AdminLayout } from './AdminLayout.vue';
export { default as useAdminRouter } from './useAdminRouter';

// 重新导出视图组件（去除登录依赖）
export {
  default as AdminHome,
  adminHomeRoutes
} from './views/AdminHome.vue';

export {
  default as AdminWorkbench,
  adminWorkbenchRoutes
} from './views/AdminWorkbench.vue';

export {
  default as AdminTools,
  adminToolsRoutes
} from './views/AdminTools.vue';
```

**文件**: `frontend_next/src/embed/AdminLayout.vue`

```vue
<template>
  <div class="admin-layout">
    <el-container>
      <!-- 左侧菜单（可收起） -->
      <el-aside
        class="sidebar"
        :width="isCollapsed ? '64px' : '200px'"
        :collapse="isCollapsed"
      >
        <div class="sidebar-header">
          <div class="logo" @click="toggleCollapse">
            <span v-if="!isCollapsed" class="logo-text">WMAI</span>
            <el-icon><Menu /></el-icon>
          </div>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapsed"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/admin/home">
            <el-icon><House /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          <el-menu-item index="/admin/workbench">
            <el-icon><Grid /></el-icon>
            <template #title>工作台</template>
          </el-menu-item>
          <el-menu-item index="/admin/tools">
            <el-icon><Tools /></el-icon>
            <template #title>工具管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容 -->
      <el-container>
        <el-header class="header">
          <div class="header-content">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>WMAI</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
            <div class="header-actions">
              <el-button circle @click="emit('close')">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </el-header>

        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Menu, House, Grid, Tools, Close } from '@element-plus/icons-vue';

const props = defineProps<{
  initialRoute?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const route = useRoute();
const router = useRouter();
const isCollapsed = ref(false);

const activeMenu = computed(() => route.path);

const titles: Record<string, string> = {
  '/admin/home': '首页',
  '/admin/workbench': '工作台',
  '/admin/tools': '工具管理',
};

const currentTitle = computed(() => {
  return titles[route.path] || '首页';
});

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<style scoped>
.admin-layout {
  height: 100%;
  width: 100%;
}

.sidebar {
  background: #f8f8f7;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
}

.sidebar-header {
  padding: 16px 12px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
}

.logo:hover {
  background: rgba(55, 53, 47, 0.08);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.sidebar-menu {
  border: none;
  background: transparent;
  padding: 12px 8px;
}

.sidebar-menu .el-menu-item {
  height: 40px;
  margin-bottom: 4px;
  border-radius: 8px;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(55, 53, 47, 0.08);
}

.header {
  background: #fff;
  height: 48px;
  padding: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.main {
  padding: 16px;
  background: #fff;
}
</style>
```

**预期结果**:
- 创建 `frontend_next/src/embed/` 目录
- 创建嵌入式 Layout 组件（去除登录依赖）
- 创建导出入口文件

---

### 步骤 3：创建简化版管理页面组件

**文件**: `frontend_next/src/embed/views/AdminHome.vue`

```vue
<template>
  <div class="admin-home">
    <div class="welcome-section">
      <h2>欢迎使用 WMAI 管理后台</h2>
      <p>您可以在这里管理系统工具和配置</p>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="工具数量" :value="toolCount" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="活跃工具" :value="activeCount" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="今日执行" :value="executionCount" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const toolCount = ref(0);
const activeCount = ref(0);
const executionCount = ref(0);

onMounted(async () => {
  // 从 store 获取统计数据
});
</script>

<style scoped>
.admin-home {
  padding: 16px;
}

.welcome-section {
  margin-bottom: 24px;
}

.welcome-section h2 {
  margin-bottom: 8px;
  color: #1a1a1a;
}

.welcome-section p {
  color: #7e7d7a;
}

.stat-card {
  margin-bottom: 16px;
}
</style>
```

**预期结果**:
- 创建简化版管理页面组件
- 组件可直接嵌入到弹框中运行

---

### 步骤 4：改造 frontend_chat - 添加依赖和配置

**文件**: `frontend_chat/package.json`

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.4.2",
    "@element-plus/icons-vue": "^2.3.2"
  }
}
```

**文件**: `frontend_chat/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@shared': resolve(__dirname, '../packages/shared-types'),
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})
```

**预期结果**:
- frontend_chat 安装 Element Plus、Vue Router、Pinia 依赖
- 配置路径别名支持 `@` 和 `@shared`

---

### 步骤 5：创建设置弹框组件

**文件**: `frontend_chat/src/components/SettingsDialog.vue`

```vue
<template>
  <el-dialog
    v-model="visible"
    title="系统设置"
    width="80%"
    :modal="true"
    :close-on-click-modal="true"
    destroy-on-close
    class="settings-dialog"
  >
    <div class="settings-container">
      <AdminLayout @close="closeSettings" />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import AdminLayout from '@/embed/AdminLayout.vue';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const visible = ref(props.modelValue);

watch(() => props.modelValue, (val) => {
  visible.value = val;
});

watch(visible, (val) => {
  emit('update:modelValue', val);
});

const closeSettings = () => {
  visible.value = false;
};
</script>

<style>
.settings-dialog {
  --el-dialog-margin-top: 5vh;
}

.settings-dialog .el-dialog__body {
  padding: 0;
  height: 70vh;
}

.settings-container {
  height: 100%;
  width: 100%;
}
</style>
```

**预期结果**:
- 创建设置弹框组件
- 弹框内嵌管理布局
- 支持关闭按钮

---

### 步骤 6：修改 App.vue 添加设置按钮和弹框

**文件**: `frontend_chat/src/App.vue`

```vue
<template>
  <div class="app-container">
    <!-- 原有布局 -->
    <Sidebar
      :conversations="conversations"
      :currentConversationId="currentConversationId"
      @new-chat="handleNewChat"
      @select="handleSelect"
      @delete="handleDelete"
    />
    <ChatWindow
      ref="chatWindowRef"
      :baseUrl="baseUrl"
      :messages="messages"
      :chatState="chatState"
      :conversationTitle="conversationTitle"
      @send-message="handleSendMessage"
      @clear-messages="clearMessages"
      @update-error="handleUpdateError"
      @update-title="handleUpdateTitle"
    />

    <!-- 设置按钮 -->
    <button class="settings-btn" @click="showSettings = true">
      <el-icon><Setting /></el-icon>
    </button>

    <!-- 设置弹框 -->
    <SettingsDialog v-model="showSettings" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Setting } from '@element-plus/icons-vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import SettingsDialog from './components/SettingsDialog.vue';
import { useChat } from './hooks/useChat';
import { useConversation } from './hooks/useConversation';

const showSettings = ref(false);
// ... 其他现有代码保持不变
</script>

<style scoped>
.settings-btn {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e5e5e5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  z-index: 100;
}

.settings-btn:hover {
  background: #f0f0f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.settings-btn .el-icon {
  font-size: 24px;
  color: #666;
}
</style>
```

**预期结果**:
- 左下角显示设置按钮
- 点击弹出设置对话框
- 对话框内显示管理页面

---

### 步骤 7：处理样式隔离

**方案**:
1. 使用 Shadow DOM 或
2. 使用 CSS Modules 前缀或
3. 使用 Element Plus 的 `ElConfigProvider` 配合 `namespace`

**推荐方案**：使用 `namespace` 前缀

```typescript
// main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus, { namespace: 'ep-chat' })

app.mount('#app')
```

在 CSS 中使用 `.ep-chat-` 前缀隔离样式。

---

## 关键文件清单

| 步骤 | 文件路径 | 操作 |
|------|----------|------|
| 1 | `packages/shared-types/index.ts` | 新建 |
| 1 | `packages/shared-types/tool.ts` | 新建 |
| 2 | `frontend_next/src/embed/index.ts` | 新建 |
| 2 | `frontend_next/src/embed/AdminLayout.vue` | 新建 |
| 2 | `frontend_next/src/embed/views/AdminHome.vue` | 新建 |
| 2 | `frontend_next/src/embed/views/AdminWorkbench.vue` | 新建 |
| 2 | `frontend_next/src/embed/views/AdminTools.vue` | 新建 |
| 3 | `frontend_chat/package.json` | 修改 |
| 3 | `frontend_chat/vite.config.ts` | 修改 |
| 4 | `frontend_chat/src/components/SettingsDialog.vue` | 新建 |
| 5 | `frontend_chat/src/App.vue` | 修改 |
| 5 | `frontend_chat/src/router/index.ts` | 新建 |
| 5 | `frontend_chat/src/stores/settings.ts` | 新建 |
| 6 | `frontend_chat/src/main.ts` | 修改 |

---

## 风险点和注意事项

1. **样式冲突**: Element Plus 在 frontend_chat 中可能与现有样式冲突
   - 解决方案：使用 `namespace` 配置隔离

2. **依赖版本不一致**: 两个项目依赖版本可能不同
   - 解决方案：共享 `package.json` 中的依赖版本

3. **路由冲突**: 两套路由系统需要独立
   - 解决方案：管理页面使用 `/admin/` 前缀

4. **构建产物**: frontend_next 需要能够作为库被引用
   - 解决方案：配置 vite 的 `lib` 模式或使用 Monorepo

---

## 验证清单

- [ ] frontend_chat 可以正常启动和聊天
- [ ] 左下角设置按钮可见
- [ ] 点击设置按钮弹出对话框
- [ ] 对话框内显示管理页面
- [ ] 管理页面菜单可切换页面
- [ ] 关闭按钮可关闭弹框
- [ ] 关闭弹框后聊天功能正常
- [ ] 样式无明显冲突

---

创建时间: 2026-02-12 16:30:00
