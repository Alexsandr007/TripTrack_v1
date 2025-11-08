// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Убираем proxy так как nginx будет обрабатывать запросы
  },
  build: {
    outDir: 'dist'
  }
})