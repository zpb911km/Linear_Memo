<template>
  <div class="auth-container">
    <div class="auth-form">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名或邮箱:</label>
          <input
            id="username"
            v-model="loginForm.username"
            type="text"
            required
            placeholder="请输入用户名或邮箱"
          />
        </div>

        <div class="form-group">
          <label for="password">密码:</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>
          还没有账户？
          <RouterLink to="/register">立即注册</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notificationStore'
import { httpClient } from '../utils/httpClient'
import { login } from '../utils/api'

const router = useRouter()
const notificationStore = useNotificationStore()

const loginForm = ref({
  username: '',
  password: '',
})

const loading = ref(false)

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    notificationStore.showError('请填写所有必填字段')
    return
  }

  loading.value = true

  try {
    const response = await login({
      username: loginForm.value.username,
      password: loginForm.value.password,
    })
    if (!response || !response.access_token) {
      notificationStore.showError('用户名或密码错误')
      return
    }
    localStorage.setItem('authToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
    httpClient.setDefaultHeaders({
      Authorization: `Bearer ${response.access_token}`,
    })
    router.push('/')
  } catch (error: any) {
    console.error('Login error:', error)
    notificationStore.showError(error.message || '登录过程中发生错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 2rem;
}

.auth-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: var(--color-card-background);
}

.auth-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-input-background);
  color: var(--color-text);
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.auth-button {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.auth-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.auth-footer a {
  color: var(--color-primary);
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
