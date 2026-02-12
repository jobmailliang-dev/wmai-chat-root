<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="visible" class="dialog-overlay" @click="handleCancel">
        <div class="dialog-container" @click.stop>
          <!-- 标题栏 -->
          <div class="dialog-header">
            <h3 class="dialog-title">{{ title }}</h3>
            <button class="close-btn" @click="handleCancel">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <!-- 消息内容 -->
          <p class="dialog-message">{{ message }}</p>

          <!-- 操作栏 -->
          <div class="dialog-actions">
            <button class="btn btn-cancel" @click="handleCancel">取消</button>
            <button class="btn btn-confirm" @click="handleConfirm">删除</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean;
  title?: string;
  message?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认删除',
  message: '确定要删除此对话吗？此操作不可恢复。',
});

const emit = defineEmits<{
  (e: 'update:visible', visible: boolean): void;
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

const handleConfirm = () => {
  emit('confirm');
  emit('update:visible', false);
};

const handleCancel = () => {
  emit('cancel');
  emit('update:visible', false);
};
</script>

<style scoped>
/* CSS Variables - 浅色主题 */
.dialog-overlay {
  --background-white: #ffffff;
  --text-primary: #1f1f1f;
  --text-secondary: rgba(0, 0, 0, 0.7);
  --text-tertiary: #8c8c8c;
  --fill-gray-light: #f5f5f5;
  --fill-gray-hover: #e8e8e8;
  --border-light: #e5e5e5;
  --icon-tertiary: #8c8c8c;
  --Button-primary-red: #ff4d4f;
  --Button-primary-red-hover: #ff7875;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-container {
  width: 360px;
  background: var(--background-white);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 20px 24px;
  position: fixed;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.15);
}

/* 标题栏 */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
}

.dialog-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: var(--fill-gray-hover);
  color: var(--text-primary);
}

/* 消息内容 */
.dialog-message {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  padding-bottom: 20px;
}

/* 操作栏 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
}

.btn-cancel {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
}

.btn-cancel:hover {
  background: var(--fill-gray-hover);
}

.btn-confirm {
  background: var(--Button-primary-red);
  color: #ffffff;
}

.btn-confirm:hover {
  background: var(--Button-primary-red-hover);
}

/* Transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-active .dialog-container,
.dialog-leave-active .dialog-container {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog-container,
.dialog-leave-to .dialog-container {
  transform: translate(-50%, -48%) scale(0.95);
  opacity: 0;
}
</style>
