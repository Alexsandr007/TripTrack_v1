<template>
  <div class="profile-block social-block">
    <h3>Социальные сети</h3>
    
    <div class="social-list">
      <div v-for="social in socialLinks" :key="social.id" class="social-item">
        <div class="social-icon">
          <span>{{ social.icon }}</span>
        </div>
        <div class="social-info">
          <span class="social-name">{{ social.name }}</span>
          <span class="social-status" :class="social.status">
            {{ social.status === 'connected' ? 'Подключено' : 'Не подключено' }}
          </span>
        </div>
        <button 
          class="social-action" 
          :class="social.status"
          @click="toggleSocial(social.id)"
        >
          {{ social.status === 'connected' ? 'Отключить' : 'Подключить' }}
        </button>
      </div>
    </div>
    
    <div class="social-benefits">
      <h4>Преимущества подключения:</h4>
      <ul>
        <li>+10% к заработку за каждую подключенную сеть</li>
        <li>Доступ к эксклюзивным заданиям</li>
        <li>Повышенный рейтинг доверия</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  name: 'SocialBlock',
  setup() {
    const socialLinks = reactive([
      { id: 1, name: 'Telegram', icon: '📱', status: 'connected' },
      { id: 2, name: 'Twitter', icon: '🐦', status: 'disconnected' },
      { id: 3, name: 'Instagram', icon: '📷', status: 'disconnected' },
      { id: 4, name: 'YouTube', icon: '🎥', status: 'connected' },
      { id: 5, name: 'TikTok', icon: '🎵', status: 'disconnected' }
    ]);

    const toggleSocial = (id) => {
      const social = socialLinks.find(s => s.id === id);
      if (social) {
        social.status = social.status === 'connected' ? 'disconnected' : 'connected';
      }
    };

    return {
      socialLinks,
      toggleSocial
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

.social-status {
  font-size: 0.8rem;
}

.social-status.connected {
  color: #4CAF50;
}

.social-status.disconnected {
  color: #f44336;
}

.social-action {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
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