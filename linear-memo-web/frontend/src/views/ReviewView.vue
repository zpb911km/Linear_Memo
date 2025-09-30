<script setup lang="ts">
import {
  fetchCards,
  fetchDeckDetail,
  fetchNextCard,
  fetchReviewCards,
  reviewAndNextCard,
  reviewCard,
} from '@/utils/api'
import type { Card, Deck } from '@/utils/types'
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import ReviewCard from '@/components/ReviewCard.vue'
import router from '@/router'

const currentCard = ref<Card | null>(null)
const currentDeck = ref<Deck | null>(null)
const isLoading = ref(true)
const total_overtime = ref(0.1)
const current_overtime = ref(0.1)

const progress = computed(() => {
  if (!currentDeck.value || !currentCard.value) return 0
  return ((total_overtime.value - current_overtime.value) / total_overtime.value) * 100
})

const handleReview = async (feedback: number) => {
  isLoading.value = true
  try {
    const next_card_info = await reviewAndNextCard(
      currentDeck.value!.id,
      currentCard.value!.id,
      feedback,
    )
    if (next_card_info === null) {
      router.push('/')
      return
    }
    if (next_card_info.overtime_count < 0.1) {
      router.push('/')
      return
    }
    current_overtime.value = next_card_info.overtime_count
    currentCard.value = next_card_info.card
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const route = useRoute()
  const deckId = Number(route.params.deckId)

  isLoading.value = true
  Promise.all([fetchDeckDetail(deckId), fetchNextCard(deckId)])
    .then(([deck, card]) => {
      currentDeck.value = deck
      total_overtime.value = deck.overtime_count
      console.log(deck.overtime_count)
      if (deck.overtime_count < 0.1) {
        router.push('/')
        return
      }
      current_overtime.value = deck.overtime_count
      currentCard.value = card
      if (!currentCard.value) {
        router.push('/')
      }
    })
    .finally(() => {
      isLoading.value = false
    })
})
</script>

<template>
  <div class="review-view">
    <div class="review-header">
      <h1 class="deck-title">Reviewing: {{ currentDeck?.name }}</h1>
      <div class="progress-indicator" v-if="currentCard">
        <span class="progress-text">Current Card</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </div>

    <div class="review-content">
      <div class="card-container" v-if="!isLoading && currentCard">
        <review-card :card="currentCard" @review="handleReview"></review-card>
      </div>

      <div class="loading-state" v-if="isLoading">
        <div class="spinner"></div>
        <p>Loading...</p>
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped>
.review-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background-color: var(--color-background);
  color: var(--color-text);
}

.review-header {
  margin-bottom: 32px;
}

.deck-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 16px;
}

.progress-indicator {
  margin-top: 16px;
}

.progress-text {
  display: block;
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.progress-bar {
  height: 8px;
  background-color: var(--color-progress-background);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(
    to right,
    var(--color-button-primary),
    var(--color-button-primary-hover)
  );
  transition: width 0.3s ease;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-radius: 50%;
  border-top-color: var(--color-button-primary);
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .review-view {
    padding: 16px;
  }

  .deck-title {
    font-size: 24px;
  }
}
</style>
