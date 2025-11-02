<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useNotificationStore } from './stores/notificationStore'
import { useThemeStore } from './stores/themeStore'
import Snackbar from './components/Snackbar.vue'
import ProgressBar from './components/ProgressBar.vue'
import { useAuthStore } from './stores/authStore'
import { onMounted, onUnmounted } from 'vue'

const notificationStore = useNotificationStore()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const onlogout = () => {
  authStore.clearAuth()
}

onMounted(() => {
  // 初始化认证状态
  authStore.initializeAuth()
})

const refreshClock = setInterval(() => {
  authStore.refreshToken().catch(() => {
    authStore.clearAuth()
  })
}, 60000)

onUnmounted(() => {
  clearInterval(refreshClock)
})
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
          <button class="logout" @click="onlogout">⏼</button>
          <button class="theme-toggle-button" @click="toggleTheme">
            {{ themeStore.theme === 'light' ? '🌙' : themeStore.theme === 'dark' ? '☀️' : '🌓' }}
          </button>
        </nav>
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
  background-color: var(--color-background);
  color: var(--color-text);
}

header {
  background-color: var(--color-navbar-background);
  color: var(--color-navbar-text);
  box-shadow: 0 2px 4px var(--color-card-shadow);
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
  flex: 1;
}

.nav-link {
  color: var(--color-navbar-text);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: var(--color-navbar-hover);
}

.nav-link.active {
  background-color: var(--color-navbar-active);
  color: white;
}

.theme-toggle-button {
  background: none;
  border: none;
  color: var(--color-navbar-text);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
  /* margin-left: auto; */
}

.logout {
  background: none;
  border: none;
  color: var(--color-navbar-text);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
  margin-left: auto;
}

.theme-toggle-button:hover {
  background-color: var(--color-navbar-hover);
}

.main-content {
  flex: 1;
  margin: 0;
  padding: 0;
  width: 100%;
}
</style>