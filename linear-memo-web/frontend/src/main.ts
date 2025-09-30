import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/themeStore'
import './assets/themes.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

// 初始化主题
const themeStore = useThemeStore(pinia)
themeStore.initTheme()

app.use(router)

app.mount('#app')
