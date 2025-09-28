<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import type { Card } from '@/utils/types'

const props = defineProps<{ card: Card }>()
const emit = defineEmits<{ (e: 'review', feedback: number): void }>()

const fliped = ref(false)
const feedback = ref(40)
let isDragging = ref(false)

const feedbackHandler = (e: MouseEvent | TouchEvent) => {
  if (isDragging.value) return
  // 检查事件类型，确保只在鼠标释放或触摸结束时触发
  if ((e instanceof MouseEvent && e.type !== 'mouseup') || (e instanceof TouchEvent && e.type !== 'touchend')) return
  fliped.value = false
  isDragging.value = false
  emit('review', feedback.value)
  feedback.value = 40
}

const koHandler = async () => {
  feedback.value = 100
  fliped.value = false
  isDragging.value = false
  emit('review', feedback.value)
  feedback.value = 40
}

const draggingHandler = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  // 确保 e.currentTarget 是 HTMLElement
  const target = e.currentTarget as HTMLElement | null
  if (!target) return // 如果 target 是 null，直接返回

  const rect = target.getBoundingClientRect()

  // 获取触摸点或鼠标点的 x 坐标
  let clientX: number;
  if (e instanceof TouchEvent) {
    clientX = e.touches[0].clientX; // 获取第一个触摸点的 clientX
  } else {
    clientX = e.clientX;
  }

  const x = clientX - rect.left
  const width = rect.width
  const percent = (x / width) * 100
  feedback.value = Math.min(Math.max(0.1, percent), 100) // 确保反馈值在0到100之间
}

const startDragging = (e: MouseEvent | TouchEvent) => {
  isDragging.value = true
  // 阻止默认行为，防止页面滚动
  if (e instanceof TouchEvent) {
    e.preventDefault();
  }
}

const stopDragging = (e: MouseEvent | TouchEvent) => {
  isDragging.value = false
  feedbackHandler(e)
}

const feedbackBarColor = computed(() => {
  const red = Math.round(255 * (1 - feedback.value / 100))
  const green = Math.round(255 * (feedback.value / 100))
  return `linear-gradient(to right, rgb(${red}, 0, ${green}), rgb(${red}, ${green}, 50))`
})

</script>
<template>
  <div class="review-card" :class="{ flipped: fliped }">
    <div class="card-front" @click="fliped = !fliped">
      <div class="card-front-inner" v-html="props.card.front"></div>
    </div>
    <div class="card-back" @click="fliped = !fliped">
      <div class="card-back-inner" v-html="props.card.back"></div>
      <div class="feedback-container">
        <div
          class="feedback-bar-container"
          @mousedown="startDragging"
          @mouseup="stopDragging"
          @mousemove="draggingHandler"
          @touchstart="startDragging"
          @touchend="stopDragging"
          @touchmove="draggingHandler"
        >
          <div class="feedback-bar" :style="{ width: `${feedback}%`, background: feedbackBarColor }">
            <div class="feedback-value">{{ feedback.toFixed(0) }}</div>
          </div>
        </div>
        <button class="btn-100" @mousedown="feedback = 100" @click="koHandler">k.o.</button>
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped>
.review-card {
  perspective: 1000px;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.card-front,
.card-back {
  width: 100%;
  height: 400px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 24px;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  position: relative;
  backface-visibility: hidden;
  margin-bottom: 20px;
  border: 1px solid var(--card-border);
}

@media (max-width: 768px) {
  .card-front,
  .card-back {
    min-height: 250px;
    padding: 16px;
  }

  .feedback-bar-container {
    height: 40px;
    margin-top: 16px;
  }
}

.card-front {
  transform: rotateY(0deg);
}

.card-back {
  transform: rotateY(180deg);
  position: absolute;
  top: 0;
  left: 0;
}

.review-card.flipped .card-front {
  transform: rotateY(180deg);
}

.review-card.flipped .card-back {
  transform: rotateY(360deg);
}

.card-front-inner,
.card-back-inner {
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  word-wrap: break-word;
  white-space: pre-wrap;
  width: 100%;
}

.card-front-inner {
  height: 100%;
}

.card-back-inner {
  height: calc(100% - 48px - 16px);
}

.feedback-container {
  width: 100%;
  height: 48px;
  background: var(--input-bg);
  border-radius: 24px;
  display: flex;
}

.feedback-bar-container {
  width: 100%;
  height: 48px;
  background: var(--input-bg);
  border-radius: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-top: auto;
  margin-bottom: 16px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--input-border);
}

.feedback-bar {
  height: 100%;
  border-radius: 24px;
  /* transition: width 0.2s ease-out; */
  position: relative;
}

.feedback-value {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-weight: bold;
  text-align: center;
  user-select: none;
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 14px;
}

.btn-100 {
  background-color: var(--button-success);
  color: white;
  border: none;
  border-radius: 12px;
}
</style>
