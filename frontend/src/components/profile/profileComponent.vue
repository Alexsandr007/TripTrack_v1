<template>
  <div class="profile-page">
    <!-- Фон страницы профиля -->
    <div class="profile-background"></div>
    
    <!-- Основной контент -->
    <div class="profile-container">
      <!-- Заголовок страницы -->
      <div class="page-header">
        <h1>Мой профиль</h1>
        <p>Управляйте вашей учетной записью и настройками</p>
      </div>

      <!-- Сетка профиля -->
      <div class="profile-grid">
        <!-- Первый ряд: Шапка профиля и Баланс -->
        <div class="grid-row">
          <div class="grid-col wide">
            <ProfileHeader />
          </div>
          <div class="grid-col">
            <BalanceBlock />
          </div>
        </div>

        <!-- Второй ряд: Информация и Реферальная система -->
        <div class="grid-row">
          <div class="grid-col">
            <ProfileInfo />
          </div>
          <div class="grid-col">
            <ReferralBlock />
          </div>
        </div>

        <!-- Третий ряд: Соцсети и Настройки -->
        <div class="grid-row">
          <div class="grid-col">
            <SocialBlock />
          </div>
          <div class="grid-col">
            <SettingsBlock />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';

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
    return {
      // Здесь можно добавить общие данные для страницы профиля
    };
  }
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  position: relative;
}

.profile-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
background: /* Темный оверлей для тени */ linear-gradient(rgb(0 0 0 / 10%), rgb(0 0 0 / 40%)), /* Ваше изображение */ url('../../assets/img/profile/profile_bg.jpg') no-repeat center center;
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

.page-header h1 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 300;
}

.page-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin: 0;
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
}

@media (max-width: 480px) {
  .profile-container {
    padding: 60px 10px 15px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}
</style>