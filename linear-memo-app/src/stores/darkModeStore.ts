// 深色模式状态管理
import { ref, watch } from 'vue'
import { invoke } from '@tauri-apps/api/core'

// 定义深色模式状态
const isDarkMode = ref(false)

// 从本地存储加载深色模式设置
const loadDarkModeSetting = async () => {
  try {
    const settings = await invoke('get_settings')
    isDarkMode.value = settings.dark_mode
  } catch (error) {
    console.error('Failed to load settings:', error)
    // 如果没有保存的设置，根据系统偏好设置
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
}

// 切换深色模式
const toggleDarkMode = async () => {
  isDarkMode.value = !isDarkMode.value
  try {
    await invoke('update_settings', { settings: { dark_mode: isDarkMode.value } })
  } catch (error) {
    console.error('Failed to save settings:', error)
  }
}

// 监听深色模式状态变化并应用到文档
watch(isDarkMode, (newVal) => {
  if (newVal) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})

// 初始化深色模式
loadDarkModeSetting()

// 导出状态和方法
export { isDarkMode, toggleDarkMode }