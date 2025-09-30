<script setup lang="ts">
import { ref } from 'vue'

// 临时数据占位
const settings = ref({
  reviewSpeed: '中等',
  reviewInterval: 1,
  reviewDays: 7,
  defaultSort: '按添加时间',
  defaultCardColor: '#4ecdc4',
})
</script>

<template>
  <div class="settings-page">
    <h1>设置</h1>
    <div class="settings-section">
      <h2>复习参数</h2>
      <div class="setting-item">
        <label>背单词速度</label>
        <select v-model="settings.reviewSpeed">
          <option>慢速</option>
          <option>中等</option>
          <option>快速</option>
        </select>
      </div>
      <div class="setting-item">
        <label>复习间隔 (天)</label>
        <input type="number" v-model="settings.reviewInterval" min="1" max="30" />
      </div>
      <div class="setting-item">
        <label>复习天数</label>
        <input type="number" v-model="settings.reviewDays" min="1" max="365" />
      </div>
    </div>
    <div class="settings-section">
      <h2>卡组参数</h2>
      <div class="setting-item">
        <label>默认排序方式</label>
        <select v-model="settings.defaultSort">
          <option>按添加时间</option>
          <option>按复习时间</option>
          <option>按掌握度</option>
        </select>
      </div>
      <div class="setting-item">
        <label>默认卡片颜色</label>
        <input type="color" v-model="settings.defaultCardColor" />
      </div>
    </div>
    <button class="save-btn">保存设置</button>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 2rem;
  background-color: var(--color-background);
  color: var(--color-text);
}

.settings-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-card-background);
  box-shadow: 0 2px 4px var(--color-card-shadow);
}

.settings-section h2 {
  margin-top: 0;
  color: var(--color-text);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.setting-item label {
  font-weight: bold;
  color: var(--color-text);
}

.setting-item input,
.setting-item select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background);
  color: var(--color-text);
}

.save-btn {
  padding: 0.5rem 1rem;
  background-color: var(--color-button-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.save-btn:hover {
  background-color: var(--color-button-primary-hover);
}
</style>
