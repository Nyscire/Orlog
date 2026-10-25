import { createApp } from 'vue'
import './assets/theme.css'
import App from './App.vue'
import { createPinia } from 'pinia'

createApp(App).use(createPinia()).mount('#app')
