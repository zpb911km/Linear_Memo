import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 从localStorage获取主题偏好，默认为'auto'
  const savedTheme = localStorage.getItem('theme') || 'auto'
  const theme = ref(savedTheme)

  // 应用主题的函数
  const applyTheme = (newTheme: string) => {
    theme.value = newTheme

    // 保存到localStorage
    localStorage.setItem('theme', newTheme)

    // 应用主题到DOM
    if (
      newTheme === 'dark' ||
      (newTheme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)
    ) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 切换主题的函数
  const toggleTheme = () => {
    if (theme.value === 'light') {
      applyTheme('dark')
    } else if (theme.value === 'dark') {
      applyTheme('auto')
    } else {
      applyTheme('light')
    }
  }

  // 监听系统主题变化
  const handleSystemThemeChange = (e: MediaQueryListEvent) => {
    if (theme.value === 'auto') {
      if (e.matches) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  // 初始化主题
  const initTheme = () => {
    applyTheme(theme.value)

    // 监听系统主题变化
    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', handleSystemThemeChange)
  }

  // 监听theme值变化并应用主题
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    theme,
    applyTheme,
    toggleTheme,
    initTheme,
  }
})
