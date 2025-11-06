<template>
  <div class="profile-block settings-block">
    <h3>Настройки</h3>
    
    <div class="settings-list">
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-name">Уведомления</span>
          <span class="setting-desc">Получать уведомления о новых заданиях</span>
        </div>
        <label class="switch">
          <input type="checkbox" v-model="settings.notifications" />
          <span class="slider"></span>
        </label>
      </div>
      
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-name">Темная тема</span>
          <span class="setting-desc">Использовать темную тему интерфейса</span>
        </div>
        <label class="switch">
          <input type="checkbox" v-model="settings.darkTheme" />
          <span class="slider"></span>
        </label>
      </div>
      
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-name">Двухфакторная аутентификация</span>
          <span class="setting-desc">Дополнительная защита аккаунта</span>
        </div>
        <label class="switch">
          <input type="checkbox" v-model="settings.twoFactorAuth" />
          <span class="slider"></span>
        </label>
      </div>
    </div>
    
    <div class="danger-zone">
      <h4>Опасная зона</h4>
      
      <!-- Кнопка выхода -->
      <button 
        class="danger-btn" 
        @click="logout" 
        :disabled="isLoggingOut"
      >
        <span v-if="isLoggingOut">Выход...</span>
        <span v-else>Выйти из аккаунта</span>
      </button>
      
      <!-- Модальное окно подтверждения выхода -->
      <div v-if="showLogoutConfirm" class="confirm-modal-overlay">
        <div class="confirm-modal">
          <h3>Подтверждение выхода</h3>
          <p>Вы уверены, что хотите выйти из аккаунта?</p>
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="cancelLogout">Отмена</button>
            <button class="confirm-btn confirm" @click="confirmLogout">Выйти</button>
          </div>
        </div>
      </div>
      
      <button class="danger-btn delete" @click="deleteAccount">Удалить аккаунт</button>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'SettingsBlock',
  setup() {
    const router = useRouter();
    const isLoggingOut = ref(false);
    const showLogoutConfirm = ref(false);

    const settings = reactive({
      notifications: true,
      darkTheme: true,
      twoFactorAuth: false
    });

    const logout = () => {
      console.log('Показать подтверждение выхода');
      showLogoutConfirm.value = true;
    };

    const cancelLogout = () => {
      console.log('Отмена выхода');
      showLogoutConfirm.value = false;
    };

    const confirmLogout = async () => {
      console.log('=== НАЧАЛО ВЫХОДА ИЗ СИСТЕМЫ ===');
      isLoggingOut.value = true;
      showLogoutConfirm.value = false;

      try {
        const token = localStorage.getItem('authToken');
        console.log('Токен для выхода:', token ? 'есть' : 'нет');

        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';

        // Отправляем запрос на сервер для выхода
        const response = await fetch(`${API_BASE}/api/auth/logout/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });

        console.log('Статус ответа выхода:', response.status);

        // Даже если сервер вернул ошибку, очищаем localStorage
        // и перенаправляем на главную
        
      } catch (error) {
        console.error('Ошибка при выходе:', error);
        // Даже при ошибке сети продолжаем выход на клиенте
      } finally {
        // Всегда очищаем localStorage и перенаправляем
        console.log('Очистка localStorage...');
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        
        console.log('Проверка очистки:');
        console.log('authToken:', localStorage.getItem('authToken'));
        console.log('user:', localStorage.getItem('user'));
        
        console.log('Перенаправление на главную страницу...');
        
        // Даем небольшую задержку для UX
        setTimeout(() => {
          router.push('/');
          // Можно также перезагрузить страницу для полного сброса состояния
          // window.location.reload();
        }, 500);
      }
    };

    const deleteAccount = () => {
      console.log('Delete account');
      // Здесь будет функционал удаления аккаунта
    };

    return {
      settings,
      isLoggingOut,
      showLogoutConfirm,
      logout,
      cancelLogout,
      confirmLogout,
      deleteAccount
    };
  }
});
</script>

<style scoped>
.settings-block h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.settings-list {
  margin-bottom: 30px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.setting-name {
  color: white;
  font-weight: 500;
}

.setting-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* Switch styles */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #25438B;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.danger-zone {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
}

.danger-zone h4 {
  color: white;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.danger-btn {
  width: 100%;
  padding: 12px;
  margin-bottom: 10px;
  background: transparent;
  border: 2px solid #f44336;
  color: #f44336;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.danger-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-btn.delete {
  border-color: #ff9800;
  color: #ff9800;
}

.danger-btn:hover:not(:disabled) {
  background: #f44336;
  color: white;
}

.danger-btn.delete:hover:not(:disabled) {
  background: #ff9800;
  color: white;
}

/* Стили для модального окна подтверждения */
.confirm-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(5px);
}

.confirm-modal {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  animation: modalAppear 0.3s ease-out;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.confirm-modal h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.4rem;
}

.confirm-modal p {
  color: #666;
  margin-bottom: 25px;
  font-size: 1rem;
}

.confirm-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.confirm-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 100px;
}

.confirm-btn.cancel {
  background: #f5f5f5;
  color: #333;
  border: 2px solid #ddd;
}

.confirm-btn.cancel:hover {
  background: #e0e0e0;
}

.confirm-btn.confirm {
  background: #f44336;
  color: white;
}

.confirm-btn.confirm:hover {
  background: #d32f2f;
}

/* Адаптивность */
@media (max-width: 768px) {
  .setting-item {
    padding: 15px;
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .confirm-modal {
    padding: 20px;
  }
  
  .confirm-actions {
    flex-direction: column;
  }
  
  .confirm-btn {
    width: 100%;
  }
}
</style>