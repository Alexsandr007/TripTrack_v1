<template>
  <div class="profile-block social-block">
    <h3>Социальные сети</h3>
    
    <div class="social-list">
      <div class="social-item">
        <div class="social-icon">
          <span>📱</span>
        </div>
        <div class="social-info">
          <span class="social-name">Telegram</span>
          <span v-if="telegramLink" class="social-link">
            {{ telegramLink }}
          </span>
          <span v-else class="social-status disconnected">
            Не подключено
          </span>
        </div>
        <button 
          class="social-action" 
          :class="telegramLink ? 'connected' : 'disconnected'"
          @click="telegramLink ? disconnectTelegram() : openTelegramModal()"
        >
          {{ telegramLink ? 'Отключить' : 'Подключить' }}
        </button>
      </div>
    </div>

    <!-- Модальное окно подключения Telegram -->
    <div v-if="showTelegramModal" class="modal-overlay" @click="closeTelegramModal">
      <div class="modal-content" @click.stop>
        <h3>Подключение Telegram</h3>
        
        <div class="telegram-form">
          <label for="telegram-link">Ссылка на ваш Telegram аккаунт:</label>
          <input
            id="telegram-link"
            v-model="telegramInput"
            type="text"
            placeholder="https://t.me/username"
            class="telegram-input"
            :class="{ error: inputError }"
          />
          <div v-if="inputError" class="error-message">
            {{ inputError }}
          </div>
          
          <div class="input-requirements">
            <p>• Введите полную ссылку на ваш Telegram аккаунт</p>
            <p>• Пример: https://t.me/username или @username</p>
            <p>• После сохранения изменить ссылку будет нельзя</p>
          </div>
        </div>
        
        <div class="modal-actions">
          <button 
            @click="saveTelegramLink" 
            :disabled="!telegramInput || saving"
            class="btn-primary"
          >
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button @click="closeTelegramModal" class="btn-secondary">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения отключения -->
    <div v-if="showDisconnectModal" class="modal-overlay" @click="closeDisconnectModal">
      <div class="modal-content" @click.stop>
        <h3>Отключение Telegram</h3>
        
        <div class="disconnect-warning">
          <p>Вы уверены, что хотите отключить Telegram?</p>
          <p class="warning-text">После отключения вы потеряете бонусы и не сможете подключить другой аккаунт!</p>
        </div>
        
        <!-- <div class="modal-actions">
          <button @click="confirmDisconnect" class="btn-danger">Отключить</button>
          <button @click="closeDisconnectModal" class="btn-secondary">Отмена</button>
        </div> -->
      </div>
    </div>
    
    
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import { useGlobalWebSocket } from '@/composables/useGlobalWebSocket';

export default defineComponent({
  name: 'SocialBlock',
  setup() {
    const { globalState, connected, sendMessage } = useGlobalWebSocket();
    
    const telegramLink = ref('');
    const showTelegramModal = ref(false);
    const showDisconnectModal = ref(false);
    const telegramInput = ref('');
    const inputError = ref('');
    const saving = ref(false);

    // Загрузка данных Telegram
    const loadTelegramData = () => {
      if (connected.value) {
        sendMessage('get_user_data');
      } else {
        // Загружаем из localStorage
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            telegramLink.value = userData.telegram_link || '';
          } catch (e) {
            console.error('Ошибка загрузки из localStorage:', e);
          }
        }
      }
    };

    // Открытие модального окна подключения
    const openTelegramModal = () => {
      if (telegramLink.value) {
        alert('Telegram уже подключен. Для изменения аккаунта обратитесь в поддержку.');
        return;
      }
      showTelegramModal.value = true;
      telegramInput.value = '';
      inputError.value = '';
    };

    // Закрытие модального окна подключения
    const closeTelegramModal = () => {
      showTelegramModal.value = false;
      telegramInput.value = '';
      inputError.value = '';
    };

    // Валидация Telegram ссылки
    const validateTelegramLink = (link) => {
      if (!link.trim()) {
        return 'Введите ссылку на Telegram аккаунт';
      }
      
      // Проверяем форматы: https://t.me/username, t.me/username, @username
      const telegramRegex = /^(https?:\/\/)?(t\.me\/|@)?[a-zA-Z0-9_]{5,32}$/;
      const cleanLink = link.trim().replace(/^https?:\/\//, '').replace(/^t\.me\//, '').replace(/^@/, '');
      
      if (!telegramRegex.test('@' + cleanLink)) {
        return 'Неверный формат ссылки. Используйте: https://t.me/username или @username';
      }
      
      return '';
    };

    // Сохранение Telegram ссылки
    const saveTelegramLink = async () => {
      const error = validateTelegramLink(telegramInput.value);
      if (error) {
        inputError.value = error;
        return;
      }

      saving.value = true;

      try {
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';

        const token = localStorage.getItem('authToken');
        
        // Очищаем и форматируем ссылку
        let cleanLink = telegramInput.value.trim();
        if (cleanLink.startsWith('@')) {
          cleanLink = 'https://t.me/' + cleanLink.slice(1);
        } else if (!cleanLink.startsWith('http')) {
          cleanLink = 'https://t.me/' + cleanLink.replace('t.me/', '');
        }

        const response = await fetch(`${API_BASE}/api/auth/save-telegram/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            telegram_link: cleanLink
          })
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.success) {
            console.log('✅ Telegram ссылка сохранена:', cleanLink);
            
            // Немедленно обновляем локальные данные
            telegramLink.value = cleanLink;
            
            // Обновляем localStorage
            const savedUser = localStorage.getItem('user');
            if (savedUser) {
              try {
                const userData = JSON.parse(savedUser);
                userData.telegram_link = cleanLink;
                localStorage.setItem('user', JSON.stringify(userData));
              } catch (e) {
                console.error('Ошибка обновления localStorage:', e);
              }
            }
            
            // Обновляем данные через WebSocket
            if (connected.value) {
              sendMessage('get_user_data');
            }
            
            closeTelegramModal();
            alert('Telegram успешно подключен!');
          } else {
            throw new Error(data.error || 'Ошибка при сохранении Telegram');
          }
        } else {
          throw new Error(`HTTP error: ${response.status}`);
        }
      } catch (err) {
        console.error('Ошибка сохранения Telegram:', err);
        alert('Ошибка при сохранении Telegram: ' + err.message);
      } finally {
        saving.value = false;
      }
    };

    // Открытие модального окна отключения
    const disconnectTelegram = () => {
      showDisconnectModal.value = true;
    };

    // Закрытие модального окна отключения
    const closeDisconnectModal = () => {
      showDisconnectModal.value = false;
    };

    // Подтверждение отключения
    const confirmDisconnect = async () => {
      try {
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';

        const token = localStorage.getItem('authToken');
        
        const response = await fetch(`${API_BASE}/api/auth/remove-telegram/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          }
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.success) {
            console.log('✅ Telegram отключен');
            
            // Немедленно обновляем локальные данные
            telegramLink.value = '';
            
            // Обновляем localStorage
            const savedUser = localStorage.getItem('user');
            if (savedUser) {
              try {
                const userData = JSON.parse(savedUser);
                userData.telegram_link = '';
                localStorage.setItem('user', JSON.stringify(userData));
              } catch (e) {
                console.error('Ошибка обновления localStorage:', e);
              }
            }
            
            // Обновляем данные через WebSocket
            if (connected.value) {
              sendMessage('get_user_data');
            }
            
            closeDisconnectModal();
            alert('Telegram отключен');
          } else {
            throw new Error(data.error || 'Ошибка при отключении Telegram');
          }
        } else {
          throw new Error(`HTTP error: ${response.status}`);
        }
      } catch (err) {
        console.error('Ошибка отключения Telegram:', err);
        alert('Ошибка при отключении Telegram: ' + err.message);
      }
    };

    // Watch для обновлений из WebSocket
    onMounted(() => {
      loadTelegramData();
    });

    // Следим за обновлениями пользователя из WebSocket
    if (globalState.user) {
      telegramLink.value = globalState.user.telegram_link || '';
    }

    return {
      telegramLink,
      showTelegramModal,
      showDisconnectModal,
      telegramInput,
      inputError,
      saving,
      openTelegramModal,
      closeTelegramModal,
      saveTelegramLink,
      disconnectTelegram,
      closeDisconnectModal,
      confirmDisconnect
    };
  }
});
</script>

<style scoped>
.social-block h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.social-list {
  margin-bottom: 25px;
}

.social-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgb(255 255 255 / 10%);
  border-radius: 10px;
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.social-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  font-size: 1.2rem;
}

.social-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.social-name {
  color: white;
  font-weight: 500;
}

.social-link {
  color: #4CAF50;
  font-size: 0.9rem;
  word-break: break-all;
}

.social-status.disconnected {
  color: #f44336;
  font-size: 0.8rem;
}

.social-action {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.social-action.connected {
  background: #f44336;
  color: white;
}

.social-action.disconnected {
  background: #4CAF50;
  color: white;
}

.social-action:hover {
  transform: scale(1.05);
}

.social-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 450px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.telegram-form {
  margin-bottom: 20px;
}

.telegram-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.telegram-input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.telegram-input:focus {
  border-color: #25438B;
  outline: none;
}

.telegram-input.error {
  border-color: #f44336;
}

.error-message {
  color: #f44336;
  font-size: 0.8rem;
  margin-top: 5px;
}

.input-requirements {
  margin-top: 10px;
  font-size: 0.8rem;
  color: #666;
}

.input-requirements p {
  margin: 3px 0;
}

.disconnect-warning {
  text-align: center;
  margin-bottom: 20px;
}

.warning-text {
  color: #f44336;
  font-weight: 500;
  margin-top: 10px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-primary {
  background: #25438B;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  background: #f44336;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.social-benefits {
  background: rgba(37, 67, 139, 0.2);
  padding: 20px;
  border-radius: 10px;
  border: 1px solid rgba(37, 67, 139, 0.3);
}

.social-benefits h4 {
  color: white;
  margin-bottom: 10px;
  font-size: 1rem;
}

.social-benefits ul {
  color: rgba(255, 255, 255, 0.8);
  padding-left: 20px;
  margin: 0;
}

.social-benefits li {
  margin-bottom: 5px;
  font-size: 0.9rem;
}
</style>