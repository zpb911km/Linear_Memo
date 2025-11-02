<template>
  <div class="auth-container">
    <div class="auth-form">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input
            id="username"
            v-model="registerForm.username"
            type="text"
            required
            placeholder="请输入用户名"
            minlength="1"
            maxlength="50"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱 (可选):</label>
          <input
            id="email"
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            maxlength="120"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码:</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            required
            placeholder="请输入密码"
            minlength="6"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码:</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            placeholder="请再次输入密码"
          />
        </div>
        <div class="form-group">
          <label for="password">执行码:</label>
          <input
            id="code"
            v-model="registerForm.code"
            type="password"
            placeholder="请输入执行码"
            maxlength="6"
          />
        </div>
        
        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>
          已有账户？
          <RouterLink to="/login">立即登录</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notificationStore'
import { httpClient } from '../utils/httpClient'
import { register } from '@/utils/api'

const router = useRouter()
const notificationStore = useNotificationStore()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  code: '',
})

const confirmPassword = ref('')

const loading = ref(false)

const handleRegister = async () => {
  // 表单验证
  if (!registerForm.username || !registerForm.password) {
    notificationStore.showError('用户名和密码是必填项')
    return
  }
  
  if (registerForm.password.length < 6) {
    notificationStore.showError('密码长度至少为6位')
    return
  }
  
  if (registerForm.password !== confirmPassword.value) {
    notificationStore.showError('两次输入的密码不一致')
    return
  }
  
  if (registerForm.email && !isValidEmail(registerForm.email)) {
    notificationStore.showError('请输入有效的邮箱地址')
    return
  }

  if (!registerForm.code) {
    notificationStore.showError('请输入执行码')
    return
  }

  loading.value = true
  
  try {
    const requestData: any = {
      username: registerForm.username,
      password: registerForm.password,
      code: registerForm.code
    }
    
    if (registerForm.email) {
      requestData.email = registerForm.email
    }
    
    const response = await register(requestData)
    if (!response || !response.access_token) {
      notificationStore.showError('注册失败!!!')
      return
    }
    localStorage.setItem('authToken', response.access_token)
    httpClient.setDefaultHeaders({
      'Authorization': `Bearer ${response.access_token}`
    })
    router.push('/')
  } catch (error: any) {
    console.error('Register error:', error)
    notificationStore.showError(error.message || '注册过程中发生错误')
  } finally {
    loading.value = false
  }
}

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
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
  margin-top: 0.5rem;
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