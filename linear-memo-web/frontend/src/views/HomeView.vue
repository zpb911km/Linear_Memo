<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()

onMounted(() => {
  // 初始化认证状态
  authStore.initializeAuth()
})
</script>

<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1>欢迎使用 Linear Memo</h1>
      <p>基于遗忘曲线的智能记忆卡片系统</p>
      
      <div class="auth-actions">
        <template v-if="authStore.isAuthenticated">
          <p>您好，{{ authStore.user?.username }}！</p>
          <RouterLink to="/decks" class="btn btn-primary">开始学习</RouterLink>
        </template>
        <template v-else>
          <p>请登录或注册以开始您的记忆之旅</p>
          <div class="button-group">
            <RouterLink to="/login" class="btn btn-primary">登录</RouterLink>
            <RouterLink to="/register" class="btn btn-secondary">注册</RouterLink>
          </div>
        </template>
      </div>
    </div>
    
    <div class="features-section">
      <div class="feature-card">
        <h3>🧠 科学算法</h3>
        <p>基于遗忘曲线理论，智能安排复习时间</p>
      </div>
      <div class="feature-card">
        <h3>⚡ 高效记忆</h3>
        <p>专注于长期记忆，提高学习效率</p>
      </div>
      <div class="feature-card">
        <h3>📱 随时随地</h3>
        <p>跨平台支持，随时随地学习</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section {
  text-align: center;
  padding: 3rem 1rem;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
  border-radius: 12px;
  color: white;
}

.welcome-section h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.welcome-section p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.auth-actions {
  margin-top: 2rem;
}

.auth-actions p {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: white;
  color: var(--color-primary);
}

.btn-primary:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.feature-card {
  background-color: var(--color-card-background);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: var(--color-primary);
}

.feature-card p {
  color: var(--color-text-secondary);
  line-height: 1.6;
}
</style>