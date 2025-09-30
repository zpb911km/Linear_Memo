<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  loading?: boolean
  progress?: number
  indeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  progress: 0,
  indeterminate: false,
})

const currentProgress = ref(0)
const isVisible = ref(false)

watch(
  () => props.loading,
  (newVal) => {
    isVisible.value = newVal
    if (newVal) {
      currentProgress.value = props.progress
    }
  },
)

watch(
  () => props.progress,
  (newVal) => {
    currentProgress.value = newVal
  },
)
</script>

<template>
  <div class="progress-container" v-if="isVisible">
    <div class="progress-bar" :class="{ indeterminate: indeterminate }">
      <div
        class="progress-fill"
        :style="{ width: indeterminate ? '100%' : `${currentProgress}%` }"
        v-if="!indeterminate"
      ></div>
      <div class="progress-indeterminate" v-if="indeterminate"></div>
    </div>
  </div>
</template>

<style scoped>
.progress-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
}

.progress-bar {
  width: 100%;
  height: 3px;
  background-color: var(--color-progress-background);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-progress-bar);
  transition: width 0.3s ease;
}

.progress-indeterminate {
  height: 100%;
  background-color: var(--color-progress-bar);
  animation: indeterminateAnimation 1s infinite linear;
  transform-origin: 0% 50%;
}

@keyframes indeterminateAnimation {
  0% {
    transform: translateX(0) scaleX(0);
  }
  40% {
    transform: translateX(0) scaleX(0.4);
  }
  100% {
    transform: translateX(100%) scaleX(0.5);
  }
}
</style>
