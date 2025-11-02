<script setup lang="ts">
import { useAuthStore } from '../stores/authStore'
import { onMounted, onUnmounted, ref } from 'vue'
import type { Deck, DeckDetail } from '@/utils/types'
import { fetchDecks, fetchDeckDetail } from '@/utils/api'
import router from '@/router'

const authStore = useAuthStore()
// 定义一个响应式变量来存储获取的牌堆详细信息
const deckDetails = ref<DeckDetail[]>([])

// 在组件挂载后获取牌堆列表并获取每个牌堆的详细信息
onMounted(async () => {
  authStore.initializeAuth()
  if (!authStore.isAuthenticated) {
    return;
  }
  try {
    const response = await fetchDecks()
    if (response) {
      console.log(response)
      for (const deck of response) {
        const detail = await fetchDeckDetail(deck.id)
        deckDetails.value.push(detail as DeckDetail)
      }
    }
  } catch (error) {
    console.error('获取牌堆详细信息时出错：', error)
  }
})

const clock = setInterval(() => {
  // 定时刷新牌堆列表
  fetchDecks()
    .then((response) => {
      if (response) {
        for (const deck of response) {
          fetchDeckDetail(deck.id).then((detail) => {
            const index = deckDetails.value.findIndex((d) => d.id === detail.id)
            if (index !== -1) {
              deckDetails.value.splice(index, 1, detail)
            } else {
              deckDetails.value.push(detail)
            }
          })
        }
      }
    })
    .catch((error) => {
      console.error('获取牌堆列表时出错：', error)
      router.push('/login')
    })
}, 60 * 1000) // 每 1 分钟刷新一次牌堆列表

onUnmounted(() => {
  clearInterval(clock)
})
</script>

<template>
  <div class="home-container">
    <div class="auth-actions">
      <template v-if="authStore.isAuthenticated">
        <div class="home-view">
          <div class="decks-list">
            <!-- 遍历每个牌堆详细信息，并使用其 id 作为唯一的键 -->
            <div v-for="deckDetail in deckDetails" :key="deckDetail.id" class="deck-item">
              <div class="deck-container">
                <h2 class="deck-name">{{ deckDetail.name }}</h2>
                <ul class="deck-info">
                  <li>卡片数量: {{ deckDetail.cards_count }}</li>
                  <li>新学数量: {{ deckDetail.new_count }}</li>
                  <li>超时数量: {{ deckDetail.overtime_count }}</li>
                  <li>复习数量: {{ deckDetail.review_count }}</li>
                  <li>记住数量: {{ deckDetail.remembered_count }}</li>
                </ul>
              </div>
              <router-link :to="{ path: `review/${deckDetail.id}` }" class="review-link"
              >复习</router-link
              >
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <h1>欢迎使用 Linear Memo</h1>
        <p>基于遗忘曲线的智能记忆卡片系统</p>
        <p>请登录或注册以开始您的记忆之旅</p>
        <div class="button-group">
          <RouterLink to="/login" class="btn btn-primary">登录</RouterLink>
          <RouterLink to="/register" class="btn btn-secondary">注册</RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: var(--color-background);
  color: var(--color-text);
}

.decks-list {
  width: 80%;
  align-items: center;
  justify-content: center;
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
}

.deck-item {
  width: 300px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px var(--color-card-shadow);
  background-color: var(--color-card-background);
}

.deck-name {
  margin-bottom: 10px;
}

.deck-info {
  list-style-type: none;
  padding: 0;
}

.review-link {
  padding: 0.5rem 1rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.review-link:hover {
  text-decoration: underline;
}

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
  background-color: rgb(12, 62, 34);
  color: var(--color-primary);
}

.btn-primary:hover {
  background-color: #095132;
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