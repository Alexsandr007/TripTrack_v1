<template>
  <div class="register-page">
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>Регистрация</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="fullName">Полное имя</label>
            <input
              id="fullName"
              v-model="form.fullName"
              type="text"
              placeholder="Введите имя"
              required
              :disabled="isLoading"
            />
          </div>
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
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="Введите ваш email"
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
          <div class="form-group">
            <label for="confirmPassword">Подтвердите пароль</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="Повторите пароль"
              required
              :disabled="isLoading"
            />
          </div>
          <div class="form-group">
            <label for="Mentorlogin">Логин Ментора</label>
            <input
              id="Mentorlogin"
              v-model="form.Mentorlogin"
              type="text"
              placeholder="Введите логин Ментора"
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
          
          <button type="submit" class="btn register-btn" :disabled="isLoading">
            {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
          </button>
        </form>
        <p class="login-link">Уже есть аккаунт? <a @click="goToLogin">Войти</a></p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, inject } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'RegisterPage',
  emits: ['register-success', 'go-to-login', 'close'],
  setup(props, { emit }) {
    const navigation = inject('navigation');
    const router = useRouter();
    
    const form = reactive({
      fullName: '',
      login: '',
      email: '',
      password: '',
      confirmPassword: '',
      Mentorlogin: ''
    });
    
    const errorMessage = ref('');
    const successMessage = ref('');
    const validationErrors = ref([]);
    const isLoading = ref(false);

    const validateForm = () => {
      const errors = [];
      
      if (!form.fullName.trim()) errors.push('Имя обязательно');
      if (!form.login.trim()) errors.push('Логин обязателен');
      if (!form.email.includes('@')) errors.push('Некорректный email');
      if (form.password.length < 6) errors.push('Пароль должен быть не менее 6 символов');
      if (form.password !== form.confirmPassword) errors.push('Пароли не совпадают');
      if (!form.Mentorlogin.trim()) errors.push('Логин Ментора обязателен');
      
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
        // Добавляем базовый URL для разработки
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';
        
        console.log('=== НАЧАЛО РЕГИСТРАЦИИ ===');
        console.log('Отправка данных на:', `${API_BASE}/api/auth/register/`);
        console.log('Данные формы:', { ...form });
        
        const response = await fetch(`${API_BASE}/api/auth/register/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fullName: form.fullName,
            login: form.login,
            email: form.email,
            password: form.password,
            confirmPassword: form.confirmPassword,
            Mentorlogin: form.Mentorlogin
          })
        });

        console.log('Статус ответа:', response.status);
        console.log('Заголовки ответа:', Object.fromEntries(response.headers.entries()));

        // Проверяем Content-Type перед парсингом JSON
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
          // Если сервер вернул не JSON, значит что-то не так с API
          const textResponse = await response.text();
          console.error('Server returned non-JSON response:', textResponse.substring(0, 500));
          throw new Error('Сервер вернул некорректный ответ. Проверьте настройки API.');
        }

        const data = await response.json();
        console.log('Ответ от сервера:', data);

        if (response.ok && data.success) {
          successMessage.value = data.message || 'Регистрация успешна!';
          
          // ВАЖНО: Сохраняем токен и данные пользователя
          console.log('Сохранение данных в localStorage...');
          
          if (data.token) {
            localStorage.setItem('authToken', data.token);
            console.log('✅ Токен сохранен:', data.token);
          } else {
            console.warn('⚠️ Токен не получен от сервера');
          }
          
          if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
            console.log('✅ Данные пользователя сохранены:', data.user);
          } else {
            console.warn('⚠️ Данные пользователя не получены от сервера');
          }
          
          // Проверяем что данные действительно сохранились
          console.log('Проверка localStorage после сохранения:');
          console.log('authToken:', localStorage.getItem('authToken'));
          console.log('user:', localStorage.getItem('user'));
          
          // Очищаем форму
          Object.keys(form).forEach(key => form[key] = '');
          
          console.log('=== УСПЕШНАЯ РЕГИСТРАЦИЯ ===');
          console.log('Перенаправление на /profile через 1.5 секунды...');
          
          // Перенаправляем на страницу профиля через 1.5 секунды
          setTimeout(() => {
            console.log('Выполняется перенаправление на /profile');
            router.push('/profile');
            emit('register-success', data.user);
          }, 1500);
          
        } else {
          // Обработка ошибок от сервера
          console.error('Ошибка регистрации:', data);
          
          if (data.errors) {
            const serverErrors = [];
            for (const field in data.errors) {
              // Преобразуем ошибки Django в читаемый формат
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
            errorMessage.value = 'Ошибка при регистрации';
          }
        }
      } catch (error) {
        console.error('Registration error:', error);
        
        if (error.message.includes('Сервер вернул некорректный ответ')) {
          errorMessage.value = error.message;
        } else if (error.message.includes('JSON')) {
          errorMessage.value = 'Проблема с API сервером. Проверьте доступность эндпоинта /api/auth/register/';
        } else {
          errorMessage.value = 'Ошибка соединения с сервером. Проверьте подключение к интернету.';
        }
      } finally {
        isLoading.value = false;
      }
    };

    const goToLogin = () => {
      emit('go-to-login');
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
      goToLogin,
      closeModal,
      navigation
    };
  }
});
</script>

<style scoped>
/* Стили остаются без изменений */
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

.register-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: url('../../../assets/img/home/jungle-bg.jpg') no-repeat center center;
  background-size: cover;
  z-index: 2000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  backdrop-filter: blur(10px);
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

.login-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-top: 15px;
}

.login-link a {
  color: #25438B;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.login-link a:hover {
  color: white;
}

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