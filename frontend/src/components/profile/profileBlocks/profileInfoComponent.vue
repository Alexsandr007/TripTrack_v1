<template>
  <div class="profile-block profile-info">
    <h3>Основная информация</h3>
    
    
    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>
    
    <div v-else>
      <div class="info-grid">
        <div class="info-item">
          <label>Логин</label>
          <div class="info-value">{{ userInfo.username || 'Не указан' }}</div>
        </div>
        
        <div class="info-item">
          <label>Почта</label>
          <div class="info-value">{{ userInfo.email || 'Не указана' }}</div>
        </div>
        
        <div class="info-item">
          <label>Полное имя</label>
          <div class="info-value">{{ userInfo.full_name || userInfo.first_name || 'Не указано' }}</div>
        </div>
        
        <div class="info-item">
          <label>Логин ментора</label>
          <div class="info-value">{{ userInfo.mentor_login || 'Не назначен' }}</div>
        </div>
        
        <div class="info-item">
          <label>Дата регистрации</label>
          <div class="info-value">{{ formattedRegistrationDate }}</div>
        </div>
        
        <div class="info-item">
          <label>Реферальный код</label>
          <div class="info-value">{{ userInfo.referral_code || 'Не сгенерирован' }}</div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { useUserProfile } from '@/composables/useUserProfile';

export default defineComponent({
  name: 'ProfileInfo',
  setup() {
    const { 
      userProfile: userInfo, 
      formattedRegistrationDate, 
      loading, 
      error, 
      connected, 
      loadUserData 
    } = useUserProfile();

    const editInfo = () => {
      console.log('Редактирование профиля');
    };

    return {
      userInfo,
      formattedRegistrationDate,
      loading,
      error,
      connected,
      loadUserData,
      editInfo
    };
  }
});
</script>

<style scoped>
.loading {
  text-align: center;
  padding: 20px;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}
.profile-info h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.info-value {
  color: white;
  font-size: 1rem;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.edit-btn {
  padding: 10px 20px;
  background: transparent;
  border: 2px solid #25438B;
  color: #25438B;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn:hover {
  background: #25438B;
  color: white;
}
</style>