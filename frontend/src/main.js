import { createApp } from 'vue'
import './assets/theme.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import { t } from './i18n'
import { applySettings } from './settings'

applySettings()

const app = createApp(App)
// $t('klucz') w każdym komponencie; zmiana języka w ustawieniach od razu odświeża teksty
app.config.globalProperties.$t = t
app.use(createPinia()).mount('#app')
