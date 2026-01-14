<template>
  <div class="profile-block profile-header">
    <!-- Статус соединения -->
    <!-- <div v-if="!connected" class="connection-warning">
      <p>Нет соединения с сервером. Данные могут быть неактуальны.</p>
      <button @click="loadUserData" class="retry-btn">Переподключиться</button>
    </div> -->
    
    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>
    
    <div v-else class="avatar-section">
      <div class="avatar">
        <!-- ИСПРАВЛЕНИЕ: правильное использование key -->
        <img 
          :src="currentAvatar" 
          alt="Аватар" 
          class="avatar-img"
          :key="avatarKey"
        />
        <button class="change-avatar-btn" @click="openAvatarUpload">
          <span>✎</span>
        </button>
      </div>
      <div class="user-info">
        <h2 class="username">{{ user.username || 'Пользователь' }}</h2>
        <p class="user-level">{{ userLevel }}</p>
      </div>
    </div>

    <!-- Модальное окно загрузки аватара -->
    <div v-if="showAvatarModal" class="modal-overlay" @click="closeAvatarModal">
      <div class="modal-content" @click.stop>
        <h3>Смена аватара</h3>
        
        <div class="avatar-upload">
          <div class="upload-area" @click="triggerFileInput">
            <div v-if="!previewAvatar" class="upload-placeholder">
              <span>📁</span>
              <p>Нажмите для выбора файла</p>
            </div>
            <img v-else :src="previewAvatar" alt="Предпросмотр" class="preview-img" />
          </div>
          
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div class="upload-requirements">
            <p>Поддерживаемые форматы: JPG, PNG, GIF</p>
            <p>Максимальный размер: 5MB</p>
          </div>
        </div>
        
        <div class="modal-actions">
          <button 
            @click="uploadAvatar" 
            :disabled="!selectedFile || uploading"
            class="btn-primary"
          >
            {{ uploading ? 'Загрузка...' : 'Сохранить' }}
          </button>
          <button @click="closeAvatarModal" class="btn-secondary">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useGlobalWebSocket } from '@/composables/useGlobalWebSocket';

export default defineComponent({
  name: 'ProfileHeader',
  setup() {
    const { globalState, connected, sendMessage } = useGlobalWebSocket();
    
    const loading = ref(false);
    const error = ref(null);
    const uploading = ref(false);
    const showAvatarModal = ref(false);
    const selectedFile = ref(null);
    const previewAvatar = ref(null);
    const fileInput = ref(null);
    const avatarKey = ref(0); // Ключ для принудительного обновления изображения

    // Реактивные данные пользователя
    const user = ref({
      username: '',
      avatar: null,
      level: 'Новичок',
      rating: '4.8',
      completedTasks: 12
    });

    // Текущий аватар с timestamp для избежания кэширования
    const currentAvatar = computed(() => {
    const avatar = user.value.avatar;
    
    // Если аватар есть и это строка
    if (avatar && typeof avatar === 'string') {
      // Если это относительный путь, добавляем базовый URL
      if (avatar.startsWith('/')) {
        // Исправляем путь: добавляем /media/ если нужно
        let correctedPath = avatar;
        if (!avatar.includes('/media/') && !avatar.startsWith('/avatars/')) {
          correctedPath = `/media/avatars${avatar}`;
        } else if (avatar.startsWith('/avatars/')) {
          correctedPath = `/media${avatar}`;
        }
        
        const timestamp = new Date().getTime();
        return `http://localhost:8000${correctedPath}?t=${timestamp}`;
      }
      // Если это уже абсолютный URL, используем как есть
      if (avatar.startsWith('http')) {
        const timestamp = new Date().getTime();
        return `${avatar}?t=${timestamp}`;
      }
    }
    
    // Во всех остальных случаях - изображение по умолчанию
    return '/img/default_profile_icon.ec8d2bdb.jpg';
  });

    // Уровень пользователя
    const userLevel = computed(() => {
      const tasks = user.value.completedTasks || 0;
      if (tasks >= 50) return 'Эксперт';
      if (tasks >= 20) return 'Продвинутый';
      if (tasks >= 10) return 'Опытный';
      return 'Новичок';
    });

    // Загрузка данных пользователя
    const loadUserData = () => {
      if (connected.value) {
        loading.value = true;
        error.value = null;
        sendMessage('get_user_data');
        
        setTimeout(() => {
          loading.value = false;
        }, 5000);
      } else {
        error.value = 'Нет соединения с сервером';
      }
    };

    // Открытие модального окна
    const openAvatarUpload = () => {
      showAvatarModal.value = true;
      selectedFile.value = null;
      previewAvatar.value = null;
    };

    // Закрытие модального окна
    const closeAvatarModal = () => {
      showAvatarModal.value = false;
      selectedFile.value = null;
      previewAvatar.value = null;
    };

    // Триггер выбора файла
    const triggerFileInput = () => {
      fileInput.value?.click();
    };

    // Обработка выбора файла
    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (!file) return;

      // Проверка типа файла
      if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите файл изображения');
        return;
      }

      // Проверка размера файла (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Файл слишком большой. Максимальный размер: 5MB');
        return;
      }

      selectedFile.value = file;

      // Создание preview
      const reader = new FileReader();
      reader.onload = (e) => {
        previewAvatar.value = e.target.result;
      };
      reader.readAsDataURL(file);
    };

    // Загрузка аватара на сервер
    // Загрузка аватара на сервер
   // Загрузка аватара на сервер
    // Загрузка аватара на сервер
    const uploadAvatar = async () => {
      if (!selectedFile.value) return;

      uploading.value = true;

      try {
        const API_BASE = process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000' 
          : '';

        const formData = new FormData();
        formData.append('avatar', selectedFile.value);

        const token = localStorage.getItem('authToken');
        
        const response = await fetch(`${API_BASE}/api/auth/update-avatar/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
          },
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          
          if (data.success) {
            console.log('✅ Аватар успешно загружен:', data.avatar_url);
            
            // НЕМЕДЛЕННО обновляем локальные данные
            user.value.avatar = data.avatar_url;
            avatarKey.value += 1;
            
            // Обновляем localStorage
            const savedUser = localStorage.getItem('user');
            if (savedUser) {
              try {
                const userData = JSON.parse(savedUser);
                userData.avatar = data.avatar_url;
                localStorage.setItem('user', JSON.stringify(userData));
              } catch (e) {
                console.error('Ошибка обновления localStorage:', e);
              }
            }
            
            closeAvatarModal();
            alert('Аватар успешно обновлен!');
            
            // НЕ запрашиваем данные через WebSocket - полагаемся на локальное обновление
            // Если нужно синхронизировать с сервером, можно сделать это позже
            setTimeout(() => {
              if (connected.value) {
                sendMessage('get_user_data');
              }
            }, 5000); // Через 5 секунд синхронизируем
            
          } else {
            throw new Error(data.error || 'Ошибка при обновлении аватара');
          }
        } else {
          throw new Error(`HTTP error: ${response.status}`);
        }
      } catch (err) {
        console.error('Ошибка загрузки аватара:', err);
        alert('Ошибка при загрузке аватара: ' + err.message);
      } finally {
        uploading.value = false;
      }
    };

    // Watch для изменений в globalState.user
    watch(() => globalState.user, (newUser) => {
      console.log('🔄 Данные пользователя обновлены:', newUser);
      if (newUser) {
        user.value = { 
          ...user.value,
          ...newUser 
        };
        loading.value = false;
        error.value = null;
        
        // Принудительно обновляем аватар при получении новых данных
        if (newUser.avatar !== user.value.avatar) {
          avatarKey.value += 1;
        }
      }
    }, { deep: true, immediate: true });

    // Watch для WebSocket соединения
    watch(connected, (newVal) => {
      console.log('🔌 WebSocket connection changed:', newVal);
      if (newVal) {
        loadUserData();
      }
    });

    onMounted(() => {
      console.log('🎯 ProfileHeader mounted');
      if (connected.value) {
        loadUserData();
      } else {
        // Загружаем из localStorage
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            user.value = { ...user.value, ...userData };
          } catch (e) {
            console.error('Ошибка загрузки из localStorage:', e);
          }
        }
      }
    });

    return {
      user,
      currentAvatar,
      userLevel,
      loading,
      error,
      connected,
      uploading,
      showAvatarModal,
      selectedFile,
      previewAvatar,
      fileInput,
      avatarKey,
      loadUserData,
      openAvatarUpload,
      closeAvatarModal,
      triggerFileInput,
      handleFileSelect,
      uploadAvatar
    };
  }
});
</script>

<style scoped>
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px;
  position: relative;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  position: relative;
  width: 80px;
  height: 80px;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #25438B;
  background: #f0f0f0;
}

.change-avatar-btn {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #25438B;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.change-avatar-btn:hover {
  background: #1a3369;
}

.user-info h2 {
  color: white;
  margin: 0 0 5px 0;
  font-size: 1.5rem;
}

.user-level {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* Модальное окно */
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
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  text-align: center;
}

.avatar-upload {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
  margin-bottom: 15px;
}

.upload-area:hover {
  border-color: #25438B;
}

.upload-placeholder span {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.preview-img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
}

.upload-requirements {
  font-size: 0.8rem;
  color: #666;
  text-align: center;
}

.upload-requirements p {
  margin: 5px 0;
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

/* Стили статусов */
.connection-warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  width: 100%;
}

.retry-btn {
  background: #fd7e14;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  margin-top: 5px;
}

.loading {
  text-align: center;
  padding: 20px;
  width: 100%;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #25438B;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  color: #c33;
  width: 100%;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>