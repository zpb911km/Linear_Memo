<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useNotificationStore } from './stores/notificationStore'
import { isDarkMode, toggleDarkMode } from './stores/darkModeStore'
import Snackbar from './components/Snackbar.vue'
import ProgressBar from './components/ProgressBar.vue'

const notificationStore = useNotificationStore()
</script>

<template>
  <div class="app-container">
    <ProgressBar
      :loading="notificationStore.progressBar.loading"
      :progress="notificationStore.progressBar.progress"
      :indeterminate="notificationStore.progressBar.indeterminate"
    />

    <header>
      <div class="header-content">
        <nav class="main-nav">
          <RouterLink to="/" class="nav-link" active-class="active">⌂</RouterLink>
          <RouterLink to="/review" class="nav-link" active-class="active">⏱</RouterLink>
          <RouterLink to="/decks" class="nav-link" active-class="active">📁</RouterLink>
          <!-- <RouterLink to="/stats" class="nav-link" active-class="active">📅</RouterLink>
          <RouterLink to="/settings" class="nav-link" active-class="active">⚙</RouterLink> -->
        </nav>
        <div class="theme-toggle">
          <button @click="toggleDarkMode" class="theme-toggle-btn">
            {{ isDarkMode ? '☀️' : '🌙' }}
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>

    <Snackbar
      :show="notificationStore.snackbar.show"
      :message="notificationStore.snackbar.message"
      :type="notificationStore.snackbar.type"
      :duration="notificationStore.snackbar.duration"
      @update:show="notificationStore.hideSnackbar"
    />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

header {
  background-color: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dark header {
  background-color: #1a2530;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
}

.main-nav {
  display: flex;
  margin: 0;
  padding: none;
}

.nav-link {
  color: #ecf0f1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: #3498db;
  color: white;
}

.dark .nav-link.active {
  background-color: #2980b9;
}

.main-content {
  flex: 1;
  margin: 0;
  padding: 0;
  width: 100%;
}

.theme-toggle {
  margin-left: auto;
}

.theme-toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.theme-toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dark .theme-toggle-btn {
  color: #ecf0f1;
}
</style>
