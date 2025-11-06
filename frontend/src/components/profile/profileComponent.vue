<template>
  <div class="profile-page">
    <!-- Загрузочный экран -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Загрузка профиля...</p>
    </div>

    <!-- Сообщение об ошибке -->
    <div v-else-if="authError" class="error-overlay">
      <div class="error-content">
        <h2>Требуется авторизация</h2>
        <p>Для просмотра профиля необходимо войти в систему</p>
        <div class="error-actions">
          <button @click="goToLogin" class="btn primary">Войти</button>
          <button @click="goToHome" class="btn secondary">На главную</button>
        </div>
      </div>
    </div>

    <!-- Основной контент профиля -->
    <div v-else>
      <!-- Фон страницы профиля -->
      <div class="profile-background"></div>
      
      <!-- Основной контент -->
      <div class="profile-container">
        <!-- Заголовок страницы -->
        <div class="page-header">
          <div class="header-actions">
            <h1>Мой профиль</h1>
          </div>
          <p>Управляйте вашей учетной записью и настройками</p>
        </div>

        <!-- Сетка профиля -->
        <div class="profile-grid">
          <!-- Первый ряд: Шапка профиля и Баланс -->
          <div class="grid-row">
            <div class="grid-col wide">
              <ProfileHeader :user="userData" />
            </div>
            <div class="grid-col">
              <BalanceBlock :user="userData" />
            </div>
          </div>

          <!-- Второй ряд: Информация и Реферальная система -->
          <div class="grid-row">
            <div class="grid-col">
              <ProfileInfo :user="userData" />
            </div>
            <div class="grid-col">
              <ReferralBlock :user="userData" />
            </div>
          </div>

          <!-- Третий ряд: Соцсети и Настройки -->
          <div class="grid-row">
            <div class="grid-col">
              <SocialBlock :user="userData" />
            </div>
            <div class="grid-col">
              <SettingsBlock :user="userData" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// Импортируем все компоненты профиля
import ProfileHeader from '@/components/profile/profileBlocks/headProfileComponent.vue';
import ProfileInfo from '@/components/profile/profileBlocks/profileInfoComponent.vue';
import BalanceBlock from '@/components/profile/profileBlocks/balanceComponent.vue';
import ReferralBlock from '@/components/profile/profileBlocks/refComponent.vue';
import SocialBlock from '@/components/profile/profileBlocks/socialComponent.vue';
import SettingsBlock from '@/components/profile/profileBlocks/settingsComponent.vue';

export default defineComponent({
  name: 'ProfilePage',
  components: {
    ProfileHeader,
    ProfileInfo,
    BalanceBlock,
    ReferralBlock,
    SocialBlock,
    SettingsBlock
  },
  setup() {
    const router = useRouter();
    const loading = ref(true);
    const authError = ref(false);
    const userData = ref(null);

    // Функция проверки авторизации
    const checkAuth = () => {
      const token = localStorage.getItem('authToken');
      const user = localStorage.getItem('user');
      
      if (token && user) {
        try {
          userData.value = JSON.parse(user);
          return true;
        } catch (e) {
          console.error('Ошибка парсинга данных пользователя:', e);
          return false;
        }
      }
      return false;
    };

    // Функция проверки авторизации на сервере
    const verifyAuthWithServer = async () => {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        return false;
      }

      try {
        console.log('Отправка запроса на проверку авторизации...');
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';
        
        const response = await fetch(`${API_BASE}/api/auth/verify/`, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });

        console.log('Статус ответа проверки:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Данные пользователя с сервера:', data);
          userData.value = data.user;
          localStorage.setItem('user', JSON.stringify(data.user));
          return true;
        } else {
          console.warn('Токен невалиден, статус:', response.status);
          // Токен невалиден, очищаем localStorage
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          return false;
        }
      } catch (error) {
        console.error('Ошибка проверки авторизации:', error);
        // В случае ошибки сети, используем локальные данные
        return checkAuth();
      }
    };

        // В главном компоненте профиля
    const logout = () => {
      console.log('Logout from main profile');
      // Очищаем localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      // Перенаправляем на главную
      router.push('/');
    };

    // Переход на страницу входа
    const goToLogin = () => {
      router.push('/login');
    };

    // Переход на главную страницу
    const goToHome = () => {
      router.push('/');
    };

    // Временная функция для отладки
    const debugAuth = () => {
      console.log('=== ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===');
      console.log('localStorage:', {
        authToken: localStorage.getItem('authToken'),
        user: localStorage.getItem('user')
      });
      
      // Принудительно устанавливаем тестовые данные
      const testUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        fullName: 'Test User'
      };
      localStorage.setItem('user', JSON.stringify(testUser));
      localStorage.setItem('authToken', 'test-token-123');
      
      console.log('После установки тестовых данных:');
      console.log('localStorage:', {
        authToken: localStorage.getItem('authToken'),
        user: localStorage.getItem('user')
      });
      
      // Перезагружаем страницу
      window.location.reload();
    };

    onMounted(async () => {
      console.log('=== Начало проверки авторизации ===');
      
      // Проверяем что в localStorage
      console.log('authToken в localStorage:', localStorage.getItem('authToken'));
      console.log('user в localStorage:', localStorage.getItem('user'));
      
      // Сначала проверяем локальные данные
      const hasLocalAuth = checkAuth();
      console.log('Локальная проверка авторизации:', hasLocalAuth);
      
      if (hasLocalAuth) {
        // Если есть локальные данные, проверяем на сервере
        const isAuthenticated = await verifyAuthWithServer();
        console.log('Проверка на сервере:', isAuthenticated);
        
        if (!isAuthenticated) {
          authError.value = true;
        }
      } else {
        console.log('Нет локальных данных авторизации');
        authError.value = true;
      }
      
      loading.value = false;
      console.log('=== Конец проверки авторизации ===');
      console.log('Результат:', {
        loading: loading.value,
        authError: authError.value,
        userData: userData.value
      });
    });

    return {
      loading,
      authError,
      userData,
      logout,
      goToLogin,
      goToHome,
      debugAuth // Добавляем функцию отладки
    };
  }
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  position: relative;
}

/* Стили для загрузочного экрана */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #25438B;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

/* Стили для экрана ошибки авторизации */
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.error-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 90%;
  color: white;
}

.error-content h2 {
  color: #ff6b6b;
  margin-bottom: 15px;
  font-size: 1.8rem;
}

.error-content p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn.primary {
  background: #25438B;
  color: white;
}

.btn.primary:hover {
  background: #1a3369;
  transform: translateY(-2px);
}

.btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

/* Обновленные стили для основного контента */
.profile-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(rgb(0 0 0 / 10%), rgb(0 0 0 / 40%)), 
              url('../../assets/img/profile/profile_bg.jpg') no-repeat center center;
  background-size: cover;
  opacity: 1;
  z-index: 1;
}

.profile-container {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 100px 20px 50px;
}

.page-header {
  text-align: center;
  margin-bottom: 50px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-actions h1 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 0;
  font-weight: 300;
  flex: 1;
  text-align: left;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.logout-icon {
  font-size: 1rem;
}

.page-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin: 0;
  text-align: left;
}

.profile-grid {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.grid-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 25px;
}

.grid-col {
  display: flex;
  flex-direction: column;
}

.grid-col.wide {
  grid-column: span 1;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .profile-container {
    padding: 80px 15px 30px;
  }
  
  .grid-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .grid-col.wide {
    grid-column: span 1;
  }

  .header-actions {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .header-actions h1 {
    text-align: center;
  }

  .page-header p {
    text-align: center;
  }
}

@media (max-width: 768px) {
  .profile-container {
    padding: 70px 10px 20px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .page-header p {
    font-size: 1rem;
  }
  
  .profile-grid {
    gap: 20px;
  }
  
  .grid-row {
    gap: 15px;
  }

  .error-content {
    padding: 30px 20px;
  }

  .error-actions {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .profile-container {
    padding: 60px 10px 15px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }

  .header-actions {
    gap: 10px;
  }

  .logout-btn {
    padding: 8px 16px;
    font-size: 0.8rem;
  }
}
</style>