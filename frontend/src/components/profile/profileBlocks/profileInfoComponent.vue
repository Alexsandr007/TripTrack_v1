<template>
  <div class="profile-block profile-info">
    <h3>Основная информация</h3>
    
    <div class="info-grid">
      <div class="info-item">
        <label>Логин</label>
        <div class="info-value">{{ userInfo.login }}</div>
      </div>
      
      <div class="info-item">
        <label>Почта</label>
        <div class="info-value">{{ userInfo.email }}</div>
      </div>
      
      <div class="info-item">
        <label>Логин ментора</label>
        <div class="info-value">{{ userInfo.mentorLogin || 'Не назначен' }}</div>
      </div>
      
      <div class="info-item">
        <label>Дата регистрации</label>
        <div class="info-value">{{ userInfo.registrationDate }}</div>
      </div>
    </div>
    
    <button class="edit-btn" @click="editInfo">Редактировать</button>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  name: 'ProfileInfo',
  setup() {
    const userInfo = reactive({
      login: 'JohnDoe',
      email: 'john@example.com',
      mentorLogin: 'SuperMentor',
      registrationDate: '15.01.2024'
    });

    const editInfo = () => {
      console.log('Edit profile info');
    };

    return {
      userInfo,
      editInfo
    };
  }
});
</script>

<style scoped>
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