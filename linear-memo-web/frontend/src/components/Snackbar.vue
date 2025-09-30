<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  show?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  duration: 3000,
  show: false,
})

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>()

const isVisible = ref(false)

const getTypeClass = () => {
  return `snackbar--${props.type}`
}

const getTypeIcon = () => {
  switch (props.type) {
    case 'success':
      return '✓'
    case 'error':
      return '✕'
    case 'warning':
      return '⚠'
    case 'info':
      return 'ℹ'
    default:
      return ''
  }
}

watch(
  () => props.show,
  (newVal) => {
    isVisible.value = newVal
    if (newVal && props.duration > 0) {
      setTimeout(() => {
        isVisible.value = false
        emit('update:show', false)
      }, props.duration)
    }
  },
)

const closeSnackbar = () => {
  isVisible.value = false
  emit('update:show', false)
}
</script>

<template>
  <div class="snackbar-container">
    <div v-if="isVisible" class="snackbar" :class="getTypeClass()">
      <span class="snackbar-icon">{{ getTypeIcon() }}</span>
      <span class="snackbar-message">{{ message }}</span>
      <button class="snackbar-close" @click="closeSnackbar">×</button>
    </div>
  </div>
</template>

<style scoped>
.snackbar-container {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.snackbar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 4px;
  box-shadow: 0 2px 8px var(--color-card-shadow);
  animation: slideUp 0.3s ease-out;
  min-width: 280px;
  max-width: 500px;
  background-color: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.snackbar-icon {
  margin-right: 8px;
  font-weight: bold;
}

.snackbar-message {
  flex: 1;
  font-size: 14px;
}

.snackbar-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: 12px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
}

.snackbar--success {
  background-color: var(--color-snackbar-success);
  color: white;
}

.snackbar--error {
  background-color: var(--color-snackbar-error);
  color: white;
}

.snackbar--warning {
  background-color: var(--color-snackbar-warning);
  color: white;
}

.snackbar--info {
  background-color: var(--color-snackbar-info);
  color: white;
}
</style>
