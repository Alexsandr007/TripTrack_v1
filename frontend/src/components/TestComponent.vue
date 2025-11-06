<template>
  <div>
    <h2>Тест связи Vue-Django</h2>
    <button @click="testGetRequest">Тест GET запроса</button>
    <button @click="testPostRequest">Тест POST запроса</button>
    <div v-if="response">
      <h3>Ответ от Django:</h3>
      <pre>{{ response }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      response: null
    }
  },
  methods: {
    async testGetRequest() {
      try {
        // Указываем полный URL до Django сервера
        const response = await fetch('http://127.0.0.1:8000/api/test/');
        const data = await response.json();
        this.response = data;
      } catch (error) {
        this.response = { error: error.message };
      }
    },
    
    async testPostRequest() {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/test/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: 'Hello from Vue!',
            user: 'test_user',
            timestamp: new Date().toISOString()
          })
        });
        const data = await response.json();
        this.response = data;
      } catch (error) {
        this.response = { error: error.message };
      }
    }
  }
}
</script>