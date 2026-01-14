<template>
  <div class="my-tours-page">
    <div class="page-header">
      <h1>🧳 Мои туры</h1>
      <p class="page-subtitle">Управление вашими бронированиями</p>
    </div>
    
    <div class="content-container">
      <div class="placeholder-card">
        <div class="placeholder-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#25438B" viewBox="0 0 16 16">
            <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5zm1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0zM1.5 4h13a.5.5 0 0 1 .5.5v1.616L8.129 7.948a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5z"/>
          </svg>
        </div>
        <h2>Раздел в разработке</h2>
        <p>Скоро здесь появится список ваших забронированных туров</p>
        
        <div class="mock-tours">
          <div class="mock-tour-card">
            <div class="mock-tour-header">
              <div class="mock-tour-title"></div>
              <div class="mock-tour-status"></div>
            </div>
            <div class="mock-tour-details">
              <div class="mock-detail"></div>
              <div class="mock-detail"></div>
              <div class="mock-detail"></div>
            </div>
          </div>
          
          <div class="mock-tour-card">
            <div class="mock-tour-header">
              <div class="mock-tour-title"></div>
              <div class="mock-tour-status"></div>
            </div>
            <div class="mock-tour-details">
              <div class="mock-detail"></div>
              <div class="mock-detail"></div>
              <div class="mock-detail"></div>
            </div>
          </div>
        </div>
        
        <div class="coming-soon-features">
          <h3>Скоро будет доступно:</h3>
          <ul>
            <li>Просмотр текущих бронирований</li>
            <li>История поездок</li>
            <li>Онлайн-чек-ин</li>
            <li>Поддержка по турам</li>
          </ul>
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
  name: 'MyToursPage',
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
.my-tours-page {
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

.mock-tours {
  margin: 30px 0;
}

.mock-tour-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(37, 67, 139, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  text-align: left;
}

.mock-tour-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.mock-tour-title {
  width: 60%;
  height: 20px;
  background: linear-gradient(90deg, rgba(37, 67, 139, 0.3), rgba(37, 67, 139, 0.1));
  border-radius: 4px;
  animation: shimmer 2s infinite;
}

.mock-tour-status {
  width: 80px;
  height: 20px;
  background: linear-gradient(90deg, rgba(37, 67, 139, 0.3), rgba(37, 67, 139, 0.1));
  border-radius: 10px;
  animation: shimmer 2s infinite 0.2s;
}

.mock-tour-details {
  display: flex;
  gap: 15px;
}

.mock-detail {
  width: 100px;
  height: 15px;
  background: linear-gradient(90deg, rgba(37, 67, 139, 0.2), rgba(37, 67, 139, 0.1));
  border-radius: 4px;
  animation: shimmer 2s infinite 0.4s;
}

@keyframes shimmer {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.7; }
}

.coming-soon-features {
  background: rgba(37, 67, 139, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin: 30px 0;
  text-align: left;
}

.coming-soon-features h3 {
  color: white;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.coming-soon-features ul {
  list-style: none;
  padding: 0;
}

.coming-soon-features li {
  color: rgba(255, 255, 255, 0.8);
  padding: 8px 0;
  padding-left: 25px;
  position: relative;
}

.coming-soon-features li:before {
  content: "→";
  position: absolute;
  left: 0;
  color: #25438B;
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
  .my-tours-page {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .placeholder-card {
    padding: 25px;
  }
  
  .mock-tour-details {
    flex-direction: column;
    gap: 10px;
  }
  
  .mock-detail {
    width: 100%;
  }
}
</style>