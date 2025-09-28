import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ReviewView from '../views/ReviewView.vue'
import DeckManagementView from '../views/DeckManagementView.vue'
import StatisticsView from '../views/StatisticsView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/review/:deckId',
      name: 'review',
      component: ReviewView,
    },
    {
      path: '/review',
      name: 'empty-review',
      redirect: '/',
    },
    {
      path: '/decks',
      name: 'decks',
      component: DeckManagementView,
    },
    {
      path: '/stats',
      name: 'stats',
      component: StatisticsView,
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
    },
  ],
})

export default router
