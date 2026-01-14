<template>
  <header class="header">
    <div class="header-content">
      <!-- Логотип слева -->
      <div class="logo" @click="goToHome">
        <img src="@/assets/img/home/logo_planet.png" alt="Logo">
      </div>
      
      <!-- Кнопки справа -->
      <div class="buttons">
        <!-- Для неавторизованных пользователей -->
        <template v-if="!isAuthenticated">
          <button class="btn login-btn" @click="goToLogin">
            <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-in-right" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M6 3.5a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 0-1 0v2A1.5 1.5 0 0 0 6.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-8A1.5 1.5 0 0 0 5 3.5v2a.5.5 0 0 0 1 0v-2z"/>
              <path fill-rule="evenodd" d="M11.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H1.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
            </svg>
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Выход...' : 'Войти' }}
          </button>
          <button class="btn register-btn" @click="goToRegister">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-plus" viewBox="0 0 16 16">
              <path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
              <path fill-rule="evenodd" d="M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z"/>
            </svg>
            Зарегистрироваться
          </button>
        </template>
        
        <!-- Для авторизованных пользователей -->
        <template v-else>
          <div class="user-info" v-if="user" @click="goToProfile">
            <div class="avatar-container">
              <img 
                v-if="user.avatar" 
                :src="user.avatar" 
                alt="Avatar" 
                class="user-avatar"
              >
              <div v-else class="avatar-placeholder">
                {{ user.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
            </div>
            <span class="username">{{ user.username }}</span>
          </div>
          
          <button class="btn find-tour-btn" @click="goToFindTour">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
            </svg>
            Найти тур
          </button>
          
          <button class="btn my-tours-btn" @click="goToMyTours">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-briefcase" viewBox="0 0 16 16">
              <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5zm1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0zM1.5 4h13a.5.5 0 0 1 .5.5v1.616L8.129 7.948a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5z"/>
            </svg>
            Мои туры
          </button>
          
          <button class="btn logout-btn" @click="handleLogout">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-right" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
              <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
            </svg>
            Выйти
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<script>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'HeaderComponent',
  setup() {
    const router = useRouter()
    const { isAuthenticated, user, logout, isLoading } = useAuth()
    const isLoggingOut = ref(false)

    const goToHome = () => {
      router.push('/')
    }

    const goToLogin = () => {
      router.push('/login')
    }

    const goToRegister = () => {
      router.push('/register')
    }

    const goToProfile = () => {
      router.push('/profile')
    }

    const goToFindTour = () => {
      // Пока что редирект на домашнюю страницу
      // Позже можно изменить на /find-tour
      router.push('/')
    }

    const goToMyTours = () => {
      // Пока что редирект на профиль
      // Позже можно изменить на /my-tours
      router.push('/profile')
    }

    const handleLogout = async () => {
      try {
        isLoggingOut.value = true
        await logout()
        // После выхода автоматически перенаправит на страницу входа
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      } finally {
        isLoggingOut.value = false
      }
    }

    // Получаем аватар пользователя
    const userAvatar = computed(() => {
      if (!user.value || !user.value.avatar) return null
      
      // Если это полный URL, используем как есть
      if (user.value.avatar.startsWith('http')) {
        return user.value.avatar
      }
      
      // Иначе добавляем базовый URL
      const baseUrl = process.env.VUE_APP_API_URL || 'http://localhost:8000'
      return `${baseUrl}${user.value.avatar}`
    })

    return {
      isAuthenticated,
      user,
      isLoading: computed(() => isLoading.value || isLoggingOut.value),
      userAvatar,
      goToHome,
      goToLogin,
      goToRegister,
      goToProfile,
      goToFindTour,
      goToMyTours,
      handleLogout
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
  background: rgba(2, 12, 43, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
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
  cursor: pointer;
}

.logo img {
  width: 40px;
  height: 40px;
  transition: transform 0.3s ease;
}

.logo img:hover {
  transform: rotate(10deg) scale(1.1);
}

.buttons {
  display: flex;
  gap: 15px;
  align-items: center;
}

.btn {
  background: rgba(255, 255, 255, 0);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.3);
  padding: 10px 15px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:hover {
  color: white;
  border-color: #25438B;
  box-shadow: 0 4px 15px rgba(37, 67, 139, 0.3);
}

.login-btn:hover {
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
}

.register-btn:hover {
  background: linear-gradient(to right, #030516 0%, #25438B 50%, #020C2B 100%);
}

.find-tour-btn:hover {
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
}

.my-tours-btn:hover {
  background: linear-gradient(to right, #030516 0%, #25438B 50%, #020C2B 100%);
}

.logout-btn:hover {
  background: linear-gradient(to right, #2b0c02 0%, #8b3c25 50%, #160503 100%);
}

/* Стили для информации о пользователе */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 50px;
  transition: background-color 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.avatar-container {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #25438B, #020C2B);
  border: 2px solid rgba(37, 67, 139, 0.5);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.username {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
}

/* Стиль для спиннера при загрузке */
.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
  margin-right: 5px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Адаптивность */
@media (max-width: 768px) {
  .header-content {
    padding: 10px 15px;
  }
  
  .btn {
    padding: 8px 12px;
    font-size: 0.8rem;
  }
  
  .logo img {
    width: 35px;
    height: 35px;
  }
  
  .username {
    display: none; /* Скрываем имя пользователя на мобильных */
  }
  
  .user-info {
    padding: 5px;
  }
  
  .avatar-container {
    width: 30px;
    height: 30px;
  }
}

@media (max-width: 480px) {
  .buttons {
    gap: 8px;
  }
  
  .btn span:not(.spinner) {
    display: none; /* Скрываем текст, оставляем только иконки */
  }
  
  .btn {
    padding: 8px;
    justify-content: center;
  }
}
</style>