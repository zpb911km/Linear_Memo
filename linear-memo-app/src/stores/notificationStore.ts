import { defineStore } from 'pinia'
import { ref } from 'vue'

// Snackbar类型定义
interface SnackbarOptions {
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

// ProgressBar类型定义
interface ProgressBarOptions {
  loading: boolean
  progress?: number
  indeterminate?: boolean
}

export const useNotificationStore = defineStore('notification', () => {
  // Snackbar状态
  const snackbar = ref({
    show: false,
    message: '',
    type: 'info' as 'success' | 'error' | 'warning' | 'info',
    duration: 3000,
  })

  // ProgressBar状态
  const progressBar = ref({
    loading: false,
    progress: 0,
    indeterminate: true,
  })

  // 显示Snackbar
  const showSnackbar = (options: SnackbarOptions) => {
    snackbar.value = {
      show: true,
      message: options.message,
      type: options.type,
      duration: options.duration || 3000,
    }
  }

  // 隐藏Snackbar
  const hideSnackbar = () => {
    snackbar.value.show = false
  }

  // 显示ProgressBar
  const showProgressBar = (options?: Partial<ProgressBarOptions>) => {
    progressBar.value = {
      loading: true,
      progress: options?.progress || 0,
      indeterminate: options?.indeterminate !== undefined ? options.indeterminate : true,
    }
  }

  // 更新ProgressBar进度
  const updateProgress = (progress: number) => {
    progressBar.value.progress = progress
    // 如果设置了具体进度值，则不是不确定进度
    if (progress > 0) {
      progressBar.value.indeterminate = false
    }
  }

  // 隐藏ProgressBar
  const hideProgressBar = () => {
    progressBar.value.loading = false
  }

  // 预设的成功消息
  const showSuccess = (message: string, duration?: number) => {
    showSnackbar({ message, type: 'success', duration })
  }

  // 预设的错误消息
  const showError = (message: string, duration?: number) => {
    showSnackbar({ message, type: 'error', duration })
  }

  // 预设的警告消息
  const showWarning = (message: string, duration?: number) => {
    showSnackbar({ message, type: 'warning', duration })
  }

  // 预设的信息消息
  const showInfo = (message: string, duration?: number) => {
    showSnackbar({ message, type: 'info', duration })
  }

  return {
    // 状态
    snackbar,
    progressBar,

    // Snackbar方法
    showSnackbar,
    hideSnackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // ProgressBar方法
    showProgressBar,
    updateProgress,
    hideProgressBar,
  }
})
