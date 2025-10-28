<template>
  <div class="register-page">
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
            />
          </div>
        
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          <button type="submit" class="btn register-btn" :disabled="isLoading">
            {{ isLoading ? 'Вход...' : 'Войти' }}
          </button>
        </form>
        <p class="login-link">Забыли пароль? <a @click="navigation.goToRecovery">Восстановить</a></p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, inject  } from 'vue';

export default defineComponent({
  name: 'LoginPage',
  emits: ['register-success', 'go-to-login', 'close'],
  setup(props, { emit }) {
    const navigation = inject('navigation')
    const form = reactive({
      login:'',
      password: '',
    });
    const errorMessage = ref('');
    const isLoading = ref(false);

    const validateForm = () => {
      if (!form.login.trim()) return 'Логин обязателен';
      if (form.password.length < 6) return 'Пароль должен быть не менее 6 символов';
      return null;
    };

    const handleSubmit = async () => {
      errorMessage.value = '';
      const validationError = validateForm();
      if (validationError) {
        errorMessage.value = validationError;
        return;
      }

      isLoading.value = true;
      // Имитация API-запроса (замените на реальный)
      setTimeout(() => {
        isLoading.value = false;
        emit('register-success', { ...form });
        // Очистка формы после успеха
        Object.keys(form).forEach(key => form[key] = '');
      }, 2000);
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
.register-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: url('../../../assets/img/home/zamok.jpg') no-repeat center center;
  background-size: cover;
  z-index: 2000; /* Выше header/footer */
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  -webkit-backdrop-filter: blur(10px);
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

.error-message {
  color: #ff6b6b;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 15px;
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
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
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

.btn:hover {
  color: white;
  border-color: #25438B;
  box-shadow: 0 4px 15px rgba(37, 67, 139, 0.3);
}

.btn:hover::before {
  left: 0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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