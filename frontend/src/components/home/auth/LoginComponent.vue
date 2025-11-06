<template>
  <div class="login-page">
    <!-- Модальное окно с blur -->
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>Вход</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="login">Логин</label>
            <input
              id="login"
              v-model="form.login"
              type="text"
              placeholder="Введите логин"
              required
              :disabled="isLoading"
            />
          </div>
          <div class="form-group">
            <label for="password">Пароль</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="Введите пароль"
              required
              :disabled="isLoading"
            />
          </div>
          
          <!-- Показываем ошибки валидации -->
          <div v-if="validationErrors" class="validation-errors">
            <p v-for="error in validationErrors" :key="error" class="error-message">
              {{ error }}
            </p>
          </div>
          
          <!-- Сообщение об успехе -->
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          
          <button type="submit" class="btn login-btn" :disabled="isLoading">
            {{ isLoading ? 'Вход...' : 'Войти' }}
          </button>
        </form>
        <p class="register-link">
          Нет аккаунта? 
          <a @click="goToRegister">Зарегистрироваться</a>
        </p>
        <p class="recovery-link">
          Забыли пароль? 
          <a @click="goToRecovery">Восстановить</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, inject } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'LoginPage',
  emits: ['login-success', 'go-to-register', 'go-to-recovery', 'close'],
  setup(props, { emit }) {
    const navigation = inject('navigation');
    const router = useRouter();
    
    const form = reactive({
      login: '',
      password: '',
    });
    
    const errorMessage = ref('');
    const successMessage = ref('');
    const validationErrors = ref([]);
    const isLoading = ref(false);

    const validateForm = () => {
      const errors = [];
      
      if (!form.login.trim()) errors.push('Логин обязателен');
      if (form.password.length < 6) errors.push('Пароль должен быть не менее 6 символов');
      
      return errors;
    };

    const handleSubmit = async () => {
      // Сбрасываем сообщения
      errorMessage.value = '';
      successMessage.value = '';
      validationErrors.value = [];
      
      // Валидация на клиенте
      const clientErrors = validateForm();
      if (clientErrors.length > 0) {
        validationErrors.value = clientErrors;
        return;
      }

      isLoading.value = true;

      try {
        console.log('=== НАЧАЛО АВТОРИЗАЦИИ В VUE ===');
        
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';
        
        console.log('Отправка данных на авторизацию:', { ...form });
        
        const response = await fetch(`${API_BASE}/api/auth/login/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            login: form.login,
            password: form.password
          })
        });

        console.log('Статус ответа:', response.status);
        console.log('Заголовки ответа:', Object.fromEntries(response.headers.entries()));

        // Проверяем Content-Type перед парсингом JSON
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
          const textResponse = await response.text();
          console.error('Server returned non-JSON response:', textResponse.substring(0, 500));
          throw new Error('Сервер вернул некорректный ответ');
        }

        const data = await response.json();
        console.log('Ответ от сервера:', data);

        if (response.ok && data.success) {
          successMessage.value = data.message || 'Авторизация успешна!';
          
          // Сохраняем токен и данные пользователя
          console.log('Сохранение данных в localStorage...');
          
          if (data.token) {
            localStorage.setItem('authToken', data.token);
            console.log('✅ Токен сохранен:', data.token);
          }
          
          if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
            console.log('✅ Данные пользователя сохранены:', data.user);
          }
          
          // Проверяем что данные сохранились
          console.log('Проверка localStorage после авторизации:');
          console.log('authToken:', localStorage.getItem('authToken'));
          console.log('user:', localStorage.getItem('user'));
          
          // Очищаем форму
          Object.keys(form).forEach(key => form[key] = '');
          
          console.log('=== УСПЕШНАЯ АВТОРИЗАЦИЯ ===');
          console.log('Перенаправление на /profile через 1.5 секунды...');
          
          // Перенаправляем на страницу профиля через 1.5 секунды
          setTimeout(() => {
            console.log('Выполняется перенаправление на /profile');
            router.push('/profile');
            emit('login-success', data.user);
          }, 1500);
          
        } else {
          // Обработка ошибок от сервера
          console.error('Ошибка авторизации:', data);
          
          if (data.errors) {
            const serverErrors = [];
            for (const field in data.errors) {
              if (Array.isArray(data.errors[field])) {
                serverErrors.push(...data.errors[field]);
              } else {
                serverErrors.push(data.errors[field]);
              }
            }
            validationErrors.value = serverErrors;
          } else if (data.error) {
            errorMessage.value = data.error;
          } else {
            errorMessage.value = 'Ошибка при авторизации';
          }
        }
      } catch (error) {
        console.error('Login error:', error);
        
        if (error.message.includes('Сервер вернул некорректный ответ')) {
          errorMessage.value = error.message;
        } else if (error.message.includes('JSON')) {
          errorMessage.value = 'Проблема с API сервером. Проверьте доступность эндпоинта /api/auth/login/';
        } else {
          errorMessage.value = 'Ошибка соединения с сервером. Проверьте подключение к интернету.';
        }
      } finally {
        isLoading.value = false;
      }
    };

    const goToRegister = () => {
      emit('go-to-register');
    };

    const goToRecovery = () => {
      emit('go-to-recovery');
    };

    const closeModal = () => {
      emit('close');
    };

    return {
      form,
      errorMessage,
      successMessage,
      validationErrors,
      isLoading,
      handleSubmit,
      goToRegister,
      goToRecovery,
      closeModal,
      navigation
    };
  }
});
</script>

<style scoped>
.login-page {
  position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: url('../../../assets/img/home/zamok.jpg') no-repeat center center;
    background-size: cover;
    z-index: 2000;
    overflow: auto;
}

.modal-overlay {
position: relative;
    top: 0;
    left: 0;
    width: 100%;
    height: 110%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px 0px;
    animation: fadeIn-4e5986ba 0.5s 
ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  backdrop-filter: blur(5px);
  border-radius: 15px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

h2 {
  text-align: center;
  color: white;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

input:focus {
  border-color: #25438B;
  box-shadow: 0 0 10px rgba(37, 67, 139, 0.5);
  outline: none;
}

input:hover {
  border-color: rgba(255, 255, 255, 0.5);
}

input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Стили для сообщений */
.success-message {
  color: #4CAF50;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 5px;
  border: 1px solid #4CAF50;
}

.validation-errors {
  margin-bottom: 15px;
}

.error-message {
  color: #ff6b6b;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 5px;
  animation: shake 0.3s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.btn {
  width: 100%;
  padding: 12px;
  border: 2px solid #ffffff80;
  background: transparent;
  color: #ffffff80;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
  transition: left 0.3s ease;
  z-index: -1;
}

.btn:hover:not(:disabled) {
  color: white;
  border-color: #25438B;
  box-shadow: 0 4px 15px rgba(37, 67, 139, 0.3);
}

.btn:hover:not(:disabled)::before {
  left: 0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  animation: none;
}

.register-link,
.recovery-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-top: 15px;
}

.register-link a,
.recovery-link a {
  color: #25438B;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.register-link a:hover,
.recovery-link a:hover {
  color: white;
}

/* Адаптивность */
@media (max-width: 768px) {
  .modal-content {
    padding: 20px;
    max-width: 350px;
  }
  
  h2 {
    font-size: 1.3rem;
  }
  
  input {
    padding: 10px;
    font-size: 0.9rem;
  }
  
  .btn {
    padding: 10px;
    font-size: 0.9rem;
  }
}
</style>