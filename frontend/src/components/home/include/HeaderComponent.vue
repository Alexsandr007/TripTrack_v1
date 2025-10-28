<template>
  <header class="header">
    <div class="header-content">
      <!-- Логотип слева -->
      <div class="logo" @click="navigation.goToHome">
        <img src="../../../assets/img/home/logo_planet.png">
      </div>
      
      <!-- Кнопки справа -->
      <div class="buttons">
        <button class="btn login-btn" @click="navigation.goToLogin">Войти</button>
        <button class="btn register-btn" @click="navigation.goToRegister">Зарегистрироваться</button>
      </div>
    </div>
  </header>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'AnyComponent',
  setup() {
    // Получаем навигацию из App.vue
    const navigation = inject('navigation')
    
    return {
      navigation
    }
  }
}
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background: rgba(2, 12, 43, 0.1); /* Прозрачный фон с оттенком из градиента */
  backdrop-filter: blur(10px); /* Размытие заднего фона */
  -webkit-backdrop-filter: blur(10px); /* Для поддержки Safari */
  z-index: 10;
  border-bottom: 1px solid rgba(37, 67, 139, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo svg {
  transition: transform 0.3s ease;
}

.logo svg:hover {
  transform: rotate(10deg) scale(1.1);
}

  .logo img {
    width: 40px;
    height: 40px;
  }

.buttons {
  display: flex;
  gap: 15px;
}

.btn {
background: rgba(255, 255, 255, 0);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.3);
    padding: 10px 15px;
    border-radius: 50px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s 
ease;
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
    display: flex
;
    align-items: center;
    gap: 5px;
}

.btn:hover {
  color: white;
  border-color: #25438B;
  box-shadow: 0 4px 15px rgba(37, 67, 139, 0.3);
}

.btn:hover::before {
  left: 0;
}

.login-btn:hover {
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
}

.register-btn:hover {
  background: linear-gradient(to right, #030516 0%, #25438B 50%, #020C2B 100%);
}

/* Адаптивность */
@media (max-width: 768px) {
  .header-content {
    padding: 10px 15px;
  }
  
  .btn {
    padding: 8px 15px;
    font-size: 0.9rem;
  }
  
  .logo img {
    width: 40px;
    height: 40px;
  }

  .logo {
    display: none;
  }
}
</style>