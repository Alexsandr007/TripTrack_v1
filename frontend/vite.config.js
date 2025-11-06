import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({  // Добавлено: функция с { mode } для условной конфигурации
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: tag => tag.includes('-')
        }
      }
    })
  ],
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
  },
  base: mode === 'production' ? '/static/' : '/',  // Добавлено: в production используем /static/ для ресурсов, в dev - /
  server: {  // Добавлено: настройки для dev сервера
    proxy: {
      '/api': {  // Прокси для API-запросов
        target: 'http://localhost:8000',  // URL Django сервера
        changeOrigin: true,  // Изменяет origin заголовка для избежания CORS
      },
    },
  },
}))