<template>
  <div class="register-page">
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>Регистрация</h2>
        
        <!-- Информация о реферале -->
        <div v-if="referralInfo" class="referral-info">
          <div class="referral-badge">
            🎁 Реферальная регистрация
          </div>
          <p class="referral-text">
            Вы регистрируетесь по приглашению от <strong>{{ referralInfo.mentor.login }}</strong>
          </p>
        </div>
        
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
            <label for="Mentorlogin">Логин Ментора *</label>
            <input
              id="Mentorlogin"
              v-model="form.Mentorlogin"
              type="text"
              placeholder="Введите логин вашего ментора"
              required
              :disabled="isLoading || isMentorAutoFilled"
            />
            <small v-if="isMentorAutoFilled" class="auto-fill-notice">
              ✅ Ментор автоматически определен из реферальной ссылки
            </small>
            <small v-else class="field-hint">
              Укажите логин пользователя, который будет вашим ментором и реферером
            </small>
          </div>
          
          <!-- Показываем ошибки валидации -->
          <div v-if="validationErrors.length > 0" class="validation-errors">
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
import { defineComponent, ref, reactive, inject, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

export default defineComponent({
  name: 'RegisterPage',
  emits: ['register-success', 'go-to-login', 'close'],
  setup(props, { emit }) {
    const navigation = inject('navigation');
    const router = useRouter();
    const route = useRoute();
    
    const form = reactive({
      fullName: '',
      login: '',
      email: '',
      password: '',
      confirmPassword: '',
      Mentorlogin: '',
      referral_code: ''
    });
    
    const errorMessage = ref('');
    const successMessage = ref('');
    const validationErrors = ref([]);
    const isLoading = ref(false);
    const referralInfo = ref(null);
    const isMentorAutoFilled = ref(false);

    // Получение информации о менторе по реферальному коду
    const getMentorByReferralCode = async (code) => {
      try {
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';
        
        console.log(`🔍 Получение информации о менторе по реферальному коду: ${code}`);
        
        const response = await fetch(`${API_BASE}/api/auth/get-mentor-by-ref/?ref=${code}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            console.log('✅ Информация о менторе получена:', data.mentor);
            return data.mentor;
          } else {
            console.warn('⚠️ API вернуло ошибку:', data.error);
          }
        } else {
          console.warn('⚠️ Ошибка HTTP:', response.status);
        }
        return null;
      } catch (error) {
        console.error('❌ Ошибка при получении информации о менторе:', error);
        return null;
      }
    };

    // Проверка реферального параметра в URL при загрузке компонента
    const checkReferralParameter = async () => {
    const refCode = route.query.ref;
    console.log('🔍 Проверка URL параметров:', route.query);
    
    if (refCode) {
      console.log(`🎯 Обнаружен реферальный код в URL: ${refCode}`);
      form.referral_code = refCode;
      
      // Получаем информацию о менторе/реферере
      const mentorInfo = await getMentorByReferralCode(refCode);
      if (mentorInfo) {
        referralInfo.value = {
          mentor: mentorInfo,
          code: refCode
        };
        
        // ✅ АВТОМАТИЧЕСКИ заполняем поле ментора логином реферера
        // Ментор и реферер - это один человек!
        form.Mentorlogin = mentorInfo.login;
        isMentorAutoFilled.value = true;
        
        console.log(`✅ Поле ментора автоматически заполнено: ${mentorInfo.login}`);
        console.log(`✅ Ментор и реферер: ${mentorInfo.login}`);
      } else {
        console.warn('⚠️ Реферальный код не найден или невалиден');
        errorMessage.value = 'Реферальный код не найден. Пожалуйста, введите логин ментора вручную.';
      }
    } else {
      console.log('ℹ️ Реферальный код не обнаружен в URL');
    }
  };

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
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';
        
        console.log('=== НАЧАЛО РЕГИСТРАЦИИ ===');
        
        // Подготавливаем данные для отправки
        const registrationData = {
          fullName: form.fullName,
          login: form.login,
          email: form.email,
          password: form.password,
          confirmPassword: form.confirmPassword,
          Mentorlogin: form.Mentorlogin
        };
        
        // Добавляем реферальный код, если он есть
        if (form.referral_code) {
          registrationData.referral_code = form.referral_code;
          console.log(`🎁 Отправка с реферальным кодом: ${form.referral_code}`);
        }
        
        console.log('Данные для регистрации:', { 
          ...registrationData,
          password: '***', // Не логируем пароль
          confirmPassword: '***'
        });
        
        const response = await fetch(`${API_BASE}/api/auth/register/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(registrationData)
        });

        console.log('Статус ответа:', response.status);

        // Проверяем Content-Type перед парсингом JSON
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
          const textResponse = await response.text();
          console.error('Server returned non-JSON response:', textResponse.substring(0, 500));
          throw new Error('Сервер вернул некорректный ответ. Проверьте настройки API.');
        }

        const data = await response.json();
        console.log('Ответ от сервера:', data);

        if (response.ok && data.success) {
          // Добавляем информацию о реферале в сообщение об успехе
          let successMsg = data.message || 'Регистрация успешна!';
          if (data.referral_info) {
            successMsg += ` Вы зарегистрированы по приглашению от ${data.referral_info.referred_by}.`;
          }
          successMessage.value = successMsg;
          
          // Сохраняем токен и данные пользователя
          if (data.token) {
            localStorage.setItem('authToken', data.token);
            console.log('✅ Токен сохранен');
          }
          
          if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
            console.log('✅ Данные пользователя сохранены');
          }
          
          // Очищаем форму
          Object.keys(form).forEach(key => form[key] = '');
          
          // Перенаправляем на страницу профиля через 1.5 секунды
          setTimeout(() => {
            router.push('/profile');
            emit('register-success', data.user);
          }, 1500);
          
        } else {
          // Обработка ошибок от сервера
          console.error('Ошибка регистрации:', data);
          
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
            errorMessage.value = 'Ошибка при регистрации';
          }
        }
      } catch (error) {
        console.error('Registration error:', error);
        errorMessage.value = 'Ошибка соединения с сервером. Проверьте подключение к интернету.';
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

    // Проверяем реферальный параметр при загрузке компонента
    onMounted(() => {
      console.log('🏗️ RegisterPage mounted');
      checkReferralParameter();
    });

    return {
      form,
      errorMessage,
      successMessage,
      validationErrors,
      isLoading,
      referralInfo,
      isMentorAutoFilled,
      handleSubmit,
      goToLogin,
      closeModal,
      navigation
    };
  }
});
</script>

<style scoped>
.referral-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.referral-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
  margin-bottom: 8px;
}

.referral-text {
  margin: 0;
  font-size: 14px;
}

.auto-fill-notice {
  color: #667eea;
  font-style: italic;
  margin-top: 5px;
  display: block;
}

.referral-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.referral-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
  margin-bottom: 8px;
}

.referral-text {
  margin: 0;
  font-size: 14px;
}

.auto-fill-notice {
  color: #667eea;
  font-style: italic;
  margin-top: 5px;
  display: block;
}

.validation-errors {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
}

.error-message {
  color: #c33;
  margin: 5px 0;
  font-size: 14px;
}

.success-message {
  background: #efe;
  border: 1px solid #cfc;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  color: #363;
}

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