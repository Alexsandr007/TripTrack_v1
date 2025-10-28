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
      <button class="danger-btn" @click="logout">Выйти из аккаунта</button>
      <button class="danger-btn delete" @click="deleteAccount">Удалить аккаунт</button>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  name: 'SettingsBlock',
  setup() {
    const settings = reactive({
      notifications: true,
      darkTheme: true,
      twoFactorAuth: false
    });

    const logout = () => {
      console.log('Logout');
    };

    const deleteAccount = () => {
      console.log('Delete account');
    };

    return {
      settings,
      logout,
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

.danger-btn.delete {
  border-color: #ff9800;
  color: #ff9800;
}

.danger-btn:hover {
  background: #f44336;
  color: white;
}

.danger-btn.delete:hover {
  background: #ff9800;
  color: white;
}
</style>