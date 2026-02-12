<template>
  <aside :class="sidebarClasses">
    <!-- 移动端遮罩 -->
    <Transition name="backdrop">
      <div v-if="showBackdrop" class="sidebar-backdrop" @click="handleBackdropClick"></div>
    </Transition>

    <!-- 侧栏主体 -->
    <div class="sidebar-main">
      <!-- Header 区 -->
      <div class="sidebar-header">
        <!-- Logo -->
        <div class="logo-wrapper" @click="handleLogoClick">
          <svg width="28" height="28" viewBox="0 0 200 200" fill="none">
            <defs>
              <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4facfe;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:1" />
              </linearGradient>
            </defs>
            <g>
              <path d="M 40 150 L 40 50 L 100 110 L 160 50 L 160 150"
                    stroke="#333" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M 70 105 L 130 105"
                    stroke="#333" stroke-width="12" stroke-linecap="round" />
              <path d="M 100 110 L 100 155"
                    stroke="url(#logo-grad)" stroke-width="14" stroke-linecap="round" />
            </g>
          </svg>
          <span v-if="showLogoText" class="logo-text">AI Chat</span>
        </div>

        <!-- 折叠/显示按钮 -->
        <button
          v-if="showCollapseBtn"
          class="collapse-btn"
          @click="handleCollapseClick"
          :title="collapseBtnTitle"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M7.63158 3.33325V16.6666M5 16.6666H15C16.3807 16.6666 17.5 15.5473 17.5 14.1666V5.83325C17.5 4.45254 16.3807 3.33325 15 3.33325H5C3.61929 3.33325 2.5 4.45254 2.5 5.83325V14.1666C2.5 15.5473 3.61929 16.6666 5 16.6666Z"
                  stroke="currentColor" stroke-width="1.5"></path>
          </svg>
        </button>
      </div>

      <!-- Body 区 -->
      <div class="sidebar-body">
        <!-- 新建对话 -->
        <button
          class="new-chat-btn"
          @click="handleNewChat"
          :disabled="isLoading"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span v-if="!isCollapsed" class="btn-text">新建对话</span>
          <span v-if="!isCollapsed" class="shortcut-hint">Ctrl+N</span>
        </button>

        <!-- 对话列表 -->
        <div v-if="!isCollapsed" class="conversation-section">
          <div v-if="!isCollapsed" class="section-title">对话历史</div>
          <div class="conversation-list">
            <template v-for="conv in conversations" :key="conv.id">
              <div
                :class="['conversation-item', { active: conv.id === currentConversationId }]"
                @click="selectConversation(conv.id)"
              >
                <div class="conv-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <span v-if="!isCollapsed" class="conv-title">{{ conv.title }}</span>

                <!-- 悬浮显示操作按钮 -->
                <button
                  v-if="!isCollapsed"
                  class="action-btn"
                  @click.stop="toggleMenu(conv.id)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="6" r="1.5"/>
                    <circle cx="12" cy="12" r="1.5"/>
                    <circle cx="12" cy="18" r="1.5"/>
                  </svg>
                </button>

                <!-- 操作菜单 -->
                <Transition name="menu">
                  <div v-if="!isCollapsed && openMenuId === conv.id" class="menu-dropdown" v-click-outside="() => openMenuId = null">
                    <div class="menu-item" @click="showRenameDialog(conv)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                      </svg>
                      重命名
                    </div>
                    <div class="menu-item delete" @click="showDeleteDialog(conv)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                      </svg>
                      删除
                    </div>
                  </div>
                </Transition>
              </div>
            </template>
          </div>

          <!-- 加载中 -->
          <div v-if="isLoading" class="loading-state">
            <span class="loading-spinner"></span>
            <span v-if="!isCollapsed">加载中...</span>
          </div>

          <!-- 空状态 -->
          <div v-if="!isLoading && conversations.length === 0" class="empty-state">
            <span v-if="isCollapsed" class="empty-icon" title="暂无对话">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </span>
            <template v-else>
              <p>暂无对话</p>
            </template>
          </div>
        </div>
      </div>

      <!-- 删除确认对话框 -->
      <ConfirmDialog
        v-model:visible="deleteDialogVisible"
        :title="`删除「${deletingConversation?.title}」`"
        message="确定要删除此对话吗？此操作不可恢复。"
        @confirm="confirmDelete"
      />

      <!-- 重命名对话框 -->
      <RenameDialog
        v-model:visible="renameDialogVisible"
        title="重命名对话"
        :defaultValue="renamingConversation?.title"
        placeholder="输入新名称"
        @confirm="confirmRename"
      />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import type { Conversation } from '../types/conversation';
import ConfirmDialog from './ConfirmDialog.vue';
import RenameDialog from './RenameDialog.vue';

interface Props {
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoading?: boolean;
  collapsed?: boolean;
}

interface Emits {
  (e: 'new-chat'): void;
  (e: 'select', id: string): void;
  (e: 'delete', id: string): void;
  (e: 'rename', id: string, newTitle: string): void;
  (e: 'toggle-sidebar'): void;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  collapsed: false,
});

const emit = defineEmits<Emits>();

// 响应式断点
const MOBILE_BREAKPOINT = 768;
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
const isMobile = computed(() => windowWidth.value < MOBILE_BREAKPOINT);

// 侧栏状态
const isCollapsed = computed(() => props.collapsed);

// 计算属性
const sidebarClasses = computed(() => ({
  sidebar: true,
  collapsed: isCollapsed.value && !isMobile.value,
  floating: isMobile.value,
  hidden: isMobile.value && isCollapsed.value,
}));

const showBackdrop = computed(() => isMobile.value && !isCollapsed.value);
const showLogoText = computed(() => !isCollapsed.value);
const showCollapseBtn = computed(() => !isCollapsed.value);
const collapseBtnTitle = computed(() => {
  if (isMobile.value) {
    return isCollapsed.value ? '打开侧边栏' : '关闭侧边栏';
  }
  return isCollapsed.value ? '展开侧边栏' : '收起侧边栏';
});

// 删除对话框状态
const deleteDialogVisible = ref(false);
const deletingConversation = ref<Conversation | null>(null);

// 重命名对话框状态
const renameDialogVisible = ref(false);
const renamingConversation = ref<Conversation | null>(null);

// 菜单状态
const openMenuId = ref<string | null>(null);

// 更新窗口宽度
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// 处理折叠按钮点击
const handleCollapseClick = () => {
  emit('toggle-sidebar');
};

// 处理遮罩层点击
const handleBackdropClick = () => {
  emit('toggle-sidebar');
};

// 点击 Logo
const handleLogoClick = () => {
  // 大屏折叠状态下点击展开
  if (!isMobile.value && isCollapsed.value) {
    emit('toggle-sidebar');
  }
  // 移动端隐藏状态下点击显示
  if (isMobile.value && isCollapsed.value) {
    emit('toggle-sidebar');
  }
};

const toggleMenu = (id: string) => {
  openMenuId.value = openMenuId.value === id ? null : id;
};

// 点击外部关闭指令
const vClickOutside = {
  mounted(el: any, binding: any) {
    el.__clickOutsideHandler__ = (event: Event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.addEventListener('click', el.__clickOutsideHandler__);
  },
  unmounted(el: any) {
    document.removeEventListener('click', el.__clickOutsideHandler__);
  },
};

const selectConversation = (id: string) => {
  emit('select', id);
  // 移动端选择后隐藏侧栏
  if (isMobile.value) {
    emit('toggle-sidebar');
  }
};

const showDeleteDialog = (conv: Conversation) => {
  deletingConversation.value = conv;
  deleteDialogVisible.value = true;
  openMenuId.value = null;
};

const confirmDelete = () => {
  if (deletingConversation.value) {
    emit('delete', deletingConversation.value.id);
  }
  deletingConversation.value = null;
};

const showRenameDialog = (conv: Conversation) => {
  renamingConversation.value = conv;
  renameDialogVisible.value = true;
  openMenuId.value = null;
};

const confirmRename = (newTitle: string) => {
  if (renamingConversation.value) {
    emit('rename', renamingConversation.value.id, newTitle);
  }
  renamingConversation.value = null;
};

const handleNewChat = () => {
  emit('new-chat');
};
</script>

<style scoped>
/* 侧栏容器 */
.sidebar {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F9FAFB;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  z-index: 50;
  width: 260px;
}

/* 大屏折叠状态 */
.sidebar.collapsed:not(.floating) {
  width: 64px;
}

/* 移动端悬浮状态 */
.sidebar.floating {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 100;
  transform: translateX(0);
  width: 260px;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.floating.hidden {
  transform: translateX(-100%);
}

/* 移动端遮罩 */
.sidebar-backdrop {
  position: fixed;
  left: 260px;
  top: 0;
  width: calc(100% - 260px);
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
  z-index: 99;
}

/* 遮罩动画 */
.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity 0.2s ease;
}

.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
}

/* 侧栏主体 */
.sidebar-main {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

/* Header 区 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: 8px;
  transition: background 0.15s;
}

.logo-wrapper:hover {
  background: rgba(0, 0, 0, 0.05);
}

.logo-wrapper:only-child {
  margin: 0;
  padding: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 600;
  color: #1A1A1A;
  white-space: nowrap;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #ADADAD;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #666;
}

/* Body 区 */
.sidebar-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
}

/* 自定义滚动条 */
.sidebar-body::-webkit-scrollbar {
  width: 4px;
}

.sidebar-body::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-body::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

.sidebar-body::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 新建对话按钮 */
.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #1A1A1A;
  transition: all 0.15s ease;
  margin-bottom: 8px;
}

.new-chat-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.06);
}

.new-chat-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.collapsed .new-chat-btn {
  justify-content: center;
  padding: 8px;
}

.btn-text {
  flex: 1;
  text-align: left;
}

.shortcut-hint {
  font-size: 12px;
  color: #999;
  opacity: 0;
  transition: opacity 0.15s;
}

.new-chat-btn:hover .shortcut-hint {
  opacity: 1;
}

/* 对话列表区域 */
.conversation-section {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.section-title {
  font-size: 12px;
  font-weight: 500;
  color: #999;
  padding: 8px 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  position: relative;
}

.conversation-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.conversation-item.active {
  background: rgba(0, 122, 255, 0.1);
}

.conversation-item.active .conv-icon,
.conversation-item.active .conv-title {
  color: #007aff;
}

.collapsed .conversation-item {
  justify-content: center;
  padding: 8px;
}

.conv-icon {
  display: flex;
  align-items: center;
  color: #666;
  flex-shrink: 0;
}

.conv-title {
  flex: 1;
  font-size: 14px;
  color: #1A1A1A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 操作按钮 */
.action-btn {
  opacity: 0;
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #999;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.conversation-item:hover .action-btn {
  opacity: 1;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #666;
}

/* 下拉菜单 */
.menu-dropdown {
  position: absolute;
  right: 8px;
  top: 100%;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 4px;
  min-width: 110px;
  z-index: 100;
  margin-top: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #1A1A1A;
  cursor: pointer;
  transition: background 0.15s;
  background: transparent;
  width: 100%;
  text-align: left;
  border: none;
}

.menu-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.menu-item.delete {
  color: #ff4d4f;
}

.menu-item.delete:hover {
  background: #fff1f0;
}

/* Menu transition */
.menu-enter-active,
.menu-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #999;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e5e5;
  border-top-color: #007aff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 20px;
  color: #999;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d9d9d9;
}

.empty-state p {
  margin: 4px 0;
  font-size: 14px;
}
</style>
