<script setup lang="ts"></script>

<template>
  <div class="stats-page">
    <h1>统计分析</h1>
    <div class="stats-section">
      <h2>每日复习情况</h2>
      <div class="chart-placeholder">
        <p>每日复习统计图 (类似GitHub贡献图)</p>
        <div class="grid-placeholder">
          <div v-for="i in 30" :key="i" class="grid-cell"></div>
        </div>
      </div>
    </div>
    <div class="stats-section">
      <h2>卡组复习情况</h2>
      <div class="deck-stats">
        <div class="deck-stat-item">
          <h3>前端开发词汇</h3>
          <p>掌握度: 85%</p>
        </div>
        <div class="deck-stat-item">
          <h3>后端开发词汇</h3>
          <p>掌握度: 70%</p>
        </div>
        <div class="deck-stat-item">
          <h3>数据库术语</h3>
          <p>掌握度: 90%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-page {
  padding: 2rem;
  background-color: var(--color-background);
  color: var(--color-text);
}

.stats-section {
  margin-bottom: 2rem;
}

.chart-placeholder {
  border: 1px dashed var(--color-border);
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--color-card-background);
  box-shadow: 0 2px 4px var(--color-card-shadow);
}

.grid-placeholder {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-top: 1rem;
}

.grid-cell {
  aspect-ratio: 1;
  background-color: var(--color-border);
  border-radius: 2px;
}

.deck-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.deck-stat-item {
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-card-background);
  box-shadow: 0 2px 4px var(--color-card-shadow);
}
</style>
