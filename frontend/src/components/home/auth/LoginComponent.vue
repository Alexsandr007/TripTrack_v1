<template>
  <div class="login-container">
    <div class="login-form">
      <h2>Вход в систему</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="login">Логин</label>
          <input
            type="text"
            id="login"
            v-model="form.login"
            required
            placeholder="Введите логин"
            :disabled="isLoading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            required
            placeholder="Введите пароль"
            :disabled="isLoading"
          />
        </div>
        
        <div class="form-group checkbox">
          <input
            type="checkbox"
            id="remember"
            v-model="form.remember"
          />
          <label for="remember">Запомнить меня</label>
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Вход...' : 'Войти' }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
      
      <div class="login-links">
        <router-link to="/register">Нет аккаунта? Зарегистрируйтесь</router-link>
        <router-link to="/recovery">Забыли пароль?</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'LoginComponent',
  setup() {
    const router = useRouter()
    const { login } = useAuth() // Убрали неиспользуемые переменные
    
    const form = reactive({
      login: '',
      password: '',
      remember: false
    })
    
    const isLoading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      try {
        isLoading.value = true
        error.value = ''
        
        const result = await login({
          username: form.login,
          password: form.password
        }, form.remember)
        
        console.log('Результат входа:', result)
        
        if (result.success) {
          // Редирект после успешного входа
          const redirect = router.currentRoute.value.query.redirect || '/profile'
          console.log('Перенаправление на:', redirect)
          router.push(redirect)
        } else {
          error.value = result.error || 'Ошибка входа'
        }
      } catch (err) {
        error.value = 'Произошла ошибка при входе'
        console.error('Login error:', err)
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      form,
      isLoading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 70px);
  padding: 20px;
  background: url('@/assets/img/home/zamok.jpg') no-repeat center center;
  background-size: cover;
}

.login-form {
  background: rgba(2, 12, 43, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(37, 67, 139, 0.3);
  border-radius: 15px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: white;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input[type="text"]:focus,
.form-group input[type="password"]:focus {
  outline: none;
  border-color: #25438B;
  box-shadow: 0 0 0 2px rgba(37, 67, 139, 0.3);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
}

.checkbox input[type="checkbox"] {
  width: auto;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(to right, #25438B, #020C2B);
  border: 1px solid rgba(37, 67, 139, 0.5);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(37, 67, 139, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.5);
  border-radius: 8px;
  color: #f8d7da;
  text-align: center;
  font-size: 0.9rem;
}

.login-links {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}

.login-links a {
  color: rgba(37, 67, 139, 0.8);
  text-decoration: none;
  transition: color 0.3s ease;
  font-size: 0.9rem;
}

.login-links a:hover {
  color: #25438B;
}

@media (max-width: 768px) {
  .login-form {
    padding: 30px 20px;
  }
  
  .login-container {
    padding: 15px;
  }
}
</style>