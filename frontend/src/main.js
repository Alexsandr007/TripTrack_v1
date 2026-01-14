import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Добавляем глобальные свойства

app.config.globalProperties.$apiUrl = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'


app.use(router)
app.mount('#app')