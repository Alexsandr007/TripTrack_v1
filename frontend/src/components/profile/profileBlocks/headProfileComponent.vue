<template>
  <div class="profile-block profile-header">
    <div class="avatar-section">
      <div class="avatar">
        <img :src="user.avatar" alt="Аватар" class="avatar-img" />
        <button class="change-avatar-btn" @click="changeAvatar">
          <span>✎</span>
        </button>
      </div>
      <div class="user-info">
        <h2 class="username">{{ user.username }}</h2>
        <p class="user-level">Уровень: {{ user.level }}</p>
      </div>
    </div>
    
    <div class="profile-stats">
      <div class="stat-item">
        <span class="stat-value">{{ user.rating }}</span>
        <span class="stat-label">Рейтинг</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ user.completedTasks }}</span>
        <span class="stat-label">Заданий</span>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  name: 'ProfileHeader',
  setup() {
    const user = reactive({
      avatar: 'http://localhost:8080/img/default_profile_icon.ec8d2bdb.jpg',
      username: 'JohnDoe',
      level: 'Новичок',
      rating: '4.8',
      completedTasks: 12
    });

    const changeAvatar = () => {
      // Логика смены аватара
      console.log('Change avatar');
    };

    return {
      user,
      changeAvatar
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

.profile-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  color: #25438B;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}
</style>