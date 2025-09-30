import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/review/:deckId',
      name: 'review',
      component: () => import('../views/ReviewView.vue'),
    },
    {
      path: '/review',
      name: 'empty-review',
      redirect: '/',
    },
    {
      path: '/decks',
      name: 'decks',
      component: () => import('../views/DeckManagementView.vue'),
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('../views/StatisticsView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
  ],
})

export default router
