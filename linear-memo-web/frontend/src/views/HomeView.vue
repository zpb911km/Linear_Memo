<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import type { Deck, DeckDetail } from '@/utils/types'
import { fetchDecks, fetchDeckDetail } from '@/utils/api'

// 定义一个响应式变量来存储获取的牌堆详细信息
const deckDetails = ref<DeckDetail[]>([])

// 在组件挂载后获取牌堆列表并获取每个牌堆的详细信息
onMounted(async () => {
  try {
    const response = await fetchDecks()
    if (response) {
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
  fetchDecks().then(response => {
    if (response) {
      for (const deck of response) {
        fetchDeckDetail(deck.id).then(detail => {
          const index = deckDetails.value.findIndex(d => d.id === detail.id)
          if (index !== -1) {
            deckDetails.value.splice(index, 1, detail)
          } else {
            deckDetails.value.push(detail)
          }
        })
      }
    }
  }).catch(error => {
    console.error('获取牌堆列表时出错：', error)
  })
}, 60 * 1000) // 每 1 分钟刷新一次牌堆列表

onUnmounted(() => {
  clearInterval(clock)
})
</script>

<template>
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
        <router-link :to="{ path: `review/${deckDetail.id}` }" class="review-link">复习</router-link>
      </div>
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
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.deck-name {
  margin-bottom: 10px;
}

.deck-info {
  list-style-type: none;
  padding: 0;
}

.review-link {
  margin-top: 10px;
  color: #007bff;
  text-decoration: none;
}

.review-link:hover {
  text-decoration: underline;
}
</style>
