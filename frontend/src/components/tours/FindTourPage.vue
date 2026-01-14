<template>
  <div class="find-tour-page">
    <div class="page-header">
      <h1>🔍 Найти тур</h1>
      <p class="page-subtitle">Здесь вы сможете найти подходящие туры</p>
    </div>
    
    <div class="content-container">
      <div class="placeholder-card">
        <div class="placeholder-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#25438B" viewBox="0 0 16 16">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
          </svg>
        </div>
        <h2>Раздел в разработке</h2>
        <p>Скоро здесь появится возможность поиска и бронирования туров</p>
        <div class="features-list">
          <div class="feature">
            <span class="feature-badge">✓</span>
            <span>Поиск по направлениям</span>
          </div>
          <div class="feature">
            <span class="feature-badge">✓</span>
            <span>Фильтры по цене и датам</span>
          </div>
          <div class="feature">
            <span class="feature-badge">✓</span>
            <span>Рейтинг и отзывы</span>
          </div>
          <div class="feature">
            <span class="feature-badge">✓</span>
            <span>Мгновенное бронирование</span>
          </div>
        </div>
        <button class="back-btn" @click="goToHome">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
          </svg>
          Вернуться на главную
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'FindTourPage',
  setup() {
    const router = useRouter()
    
    const goToHome = () => {
      router.push('/')
    }
    
    return {
      goToHome
    }
  }
}
</script>

<style scoped>
.find-tour-page {
  min-height: calc(100vh);
  background: linear-gradient(135deg, #020C2B 0%, #030516 50%, #25438B 100%);
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 20px;
}

.page-header h1 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 10px;
  background: linear-gradient(to right, #fff, #25438B);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
}

.content-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.placeholder-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(37, 67, 139, 0.3);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.placeholder-icon {
  margin-bottom: 30px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.placeholder-card h2 {
  color: white;
  font-size: 2rem;
  margin-bottom: 15px;
}

.placeholder-card p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 30px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 30px 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  padding: 10px 15px;
  background: rgba(37, 67, 139, 0.2);
  border-radius: 10px;
  border-left: 3px solid #25438B;
}

.feature-badge {
  background: #25438B;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.back-btn {
  background: linear-gradient(to right, #25438B, #020C2B);
  border: 1px solid rgba(37, 67, 139, 0.5);
  color: white;
  padding: 12px 25px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(37, 67, 139, 0.3);
  background: linear-gradient(to right, #2d4f9e, #031137);
}

@media (max-width: 768px) {
  .find-tour-page {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .placeholder-card {
    padding: 25px;
  }
  
  .features-list {
    gap: 10px;
  }
  
  .feature {
    font-size: 0.9rem;
    padding: 8px 12px;
  }
}
</style>