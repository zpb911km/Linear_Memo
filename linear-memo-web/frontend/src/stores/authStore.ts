import { defineStore } from 'pinia'
import { ref } from 'vue'
import { httpClient } from '../utils/httpClient'
import type { User } from '../utils/types'
import router from '@/router'


export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const token = ref<string | null>(null)

  // 初始化认证状态
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('authToken')
    if (savedToken) {
      token.value = savedToken
      isAuthenticated.value = true
      httpClient.setDefaultHeaders({
        Authorization: `Bearer ${savedToken}`,
      })
      // 加载用户信息
      loadUserInfo()
    }
  }

  // 设置认证信息
  const setAuth = (authToken: string, refreshToken: string, userData: User) => {
    token.value = authToken
    user.value = userData
    isAuthenticated.value = true

    // 保存到localStorage
    localStorage.setItem('authToken', authToken)
    localStorage.setItem('refreshToken', refreshToken)

    // 设置HTTP客户端默认头部
    httpClient.setDefaultHeaders({
      Authorization: `Bearer ${authToken}`,
    })
  }

  // 清除认证信息
  const clearAuth = () => {
    token.value = null
    user.value = null
    isAuthenticated.value = false

    // 从localStorage移除
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')

    // 清除HTTP客户端认证头部
    const headers = httpClient.headers
    delete headers['Authorization']
    httpClient.setDefaultHeaders(headers)

    router.push('/login')
  }

  // 加载用户信息
  const loadUserInfo = async () => {
    try {
      if (!token.value) return

      const response = await httpClient.get<{ user: User }>('/api/user/profile')
      if (response.data?.user) {
        user.value = response.data.user
        isAuthenticated.value = true
      }
    } catch (error) {
      console.error('Failed to load user info:', error)
      // 如果获取用户信息失败，清除认证状态
      clearAuth()
    }
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      // httpClient.setDefaultHeaders({
      //   'Authorization': `Bearer ${refreshToken}`
      // })
      if (!refreshToken) return
      const response = await httpClient.post<{ access_token: string }>('/refresh', '', {
        Authorization: `Bearer ${refreshToken}`,
      })
      if (response.data?.access_token) {
        token.value = response.data.access_token
        // 刷新HTTP客户端认证头部
        const headers = httpClient.headers
        headers['Authorization'] = `Bearer ${token.value}`
        localStorage.setItem('authToken', token.value)
      }
    } catch (error) {
      console.error('Failed to refresh token:', error)
      // 如果刷新令牌失败，清除认证状态
      clearAuth()
    }
    // finally {
    //   const access_token = localStorage.getItem('authToken')
    //   httpClient.setDefaultHeaders({
    //     'Authorization': `Bearer ${access_token}`
    //   })
    // }
  }

  // 登出
  const logout = () => {
    clearAuth()
  }

  return {
    user,
    isAuthenticated,
    token,
    setAuth,
    clearAuth,
    loadUserInfo,
    logout,
    initializeAuth,
    refreshToken,
  }
})
