<template>
  <div>
    <h1>Тест API</h1>
    <button @click="testApi">Тест API</button>
    <button @click="testAuth">Тест авторизации</button>
    <div v-if="message">{{ message }}</div>
    <div v-if="error" style="color: red">{{ error }}</div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAxios } from '@/composables/useAxios'

export default {
  name: 'TestComponent',
  setup() {
    const { api } = useAxios()
    const message = ref('')
    const error = ref('')

    const testApi = async () => {
      try {
        const response = await api.get('/test/')
        message.value = 'API работает: ' + JSON.stringify(response.data)
        error.value = ''
      } catch (err) {
        error.value = 'Ошибка API: ' + err.message
        message.value = ''
      }
    }

    const testAuth = async () => {
      try {
        const response = await api.get('/auth/verify/')
        message.value = 'Авторизация работает: ' + JSON.stringify(response.data)
        error.value = ''
      } catch (err) {
        error.value = 'Ошибка авторизации: ' + err.message
        message.value = ''
      }
    }

    return {
      message,
      error,
      testApi,
      testAuth
    }
  }
}
</script>