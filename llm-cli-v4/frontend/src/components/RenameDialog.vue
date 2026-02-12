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

          <!-- 内容区 -->
          <div class="dialog-content">
            <p class="dialog-hint">输入新的对话名称</p>
            <div class="input-wrapper">
              <input
                ref="inputRef"
                v-model="inputValue"
                class="dialog-input"
                :placeholder="placeholder"
                @keydown.enter="handleConfirm"
              />
              <button
                v-if="inputValue"
                class="clear-btn"
                @click="inputValue = ''"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>

          <!-- 操作栏 -->
          <div class="dialog-actions">
            <button class="btn btn-cancel" @click="handleCancel">取消</button>
            <button class="btn btn-confirm" @click="handleConfirm">保存</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';

interface Props {
  visible: boolean;
  title?: string;
  placeholder?: string;
  defaultValue?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: '重命名',
  placeholder: '输入新名称',
});

const emit = defineEmits<{
  (e: 'update:visible', visible: boolean): void;
  (e: 'confirm', value: string): void;
  (e: 'cancel'): void;
}>();

const inputValue = ref(props.defaultValue || '');
const inputRef = ref<HTMLInputElement | null>(null);

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      inputValue.value = props.defaultValue || '';
      nextTick(() => {
        inputRef.value?.focus();
      });
    }
  }
);

const handleConfirm = () => {
  if (inputValue.value.trim()) {
    emit('confirm', inputValue.value.trim());
    emit('update:visible', false);
  }
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
  --Button-primary-blue: #007aff;
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
  width: 400px;
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
  padding-top: 4px;
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

/* 内容区 */
.dialog-content {
  padding: 0;
}

.dialog-hint {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: var(--text-tertiary);
}

.input-wrapper {
  position: relative;
  background: var(--fill-gray-light);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  transition: border-color 0.15s ease;
}

.input-wrapper:focus-within {
  border-color: var(--Button-primary-blue);
}

.dialog-input {
  width: 100%;
  padding: 10px 36px 10px 14px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
}

.dialog-input::placeholder {
  color: var(--text-tertiary);
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--icon-tertiary);
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s ease;
}

.input-wrapper:hover .clear-btn {
  opacity: 1;
}

.clear-btn:hover {
  background: var(--fill-gray-hover);
  color: var(--text-primary);
}

/* 操作栏 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 20px;
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
  background: var(--Button-primary-blue);
  color: #ffffff;
}

.btn-confirm:hover {
  background: #0056b3;
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
