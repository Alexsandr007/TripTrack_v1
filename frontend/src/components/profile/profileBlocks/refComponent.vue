<template>
  <div class="ref-component profile-block">
    <h3>Реферальная система</h3>
    
    <!-- Статус соединения -->
    <div v-if="!connected" class="connection-warning">
      <p>Нет соединения с сервером. Данные могут быть неактуальны.</p>
      <button @click="loadReferralStats" class="retry-btn">Переподключиться</button>
    </div>
    
    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>
    
    <!-- Ошибка -->
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="loadReferralStats" class="retry-btn">Повторить</button>
    </div>
    
    <div v-else>
      <div class="referral-stats">
        <div class="stat">
          <span class="stat-number">{{ displayStats.total_referrals }}</span>
          <span class="stat-label">Всего рефералов</span>
        </div>
        <div class="stat">
          <span class="stat-number">0</span>
          <span class="stat-label">Активных</span>
        </div>
        <div class="stat">
          <span class="stat-number">{{ displayStats.referral_balance }}</span>
          <span class="stat-label">Заработано</span>
        </div>
      </div>
      
      <div class="referral-link">
        <label>Ваша реферальная ссылка:</label>
        <div class="link-container">
          <input :value="displayLink" readonly class="link-input" />
          <button @click="copyReferralLink" class="copy-btn">📋</button>
        </div>
        <p class="referral-hint">Отправьте эту ссылку друзьям. При их регистрации вы получите бонус!</p>
        
        <!-- Индикатор обновления -->
        <div v-if="justUpdated" class="update-indicator">
          ✅ Данные обновлены
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useReferralSystem } from '@/composables/useReferralSystem';
import { useGlobalWebSocket } from '@/composables/useGlobalWebSocket';

export default {
  name: 'RefComponent',
  setup() {
    const debugInfo = ref(true);
    const justUpdated = ref(false);
    const lastUpdate = ref(null);
    
    const { 
      referralStats, 
      referralLink, 
      loading, 
      error, 
      loadReferralStats, 
      copyReferralLink 
    } = useReferralSystem();
    
    const { connected, globalState } = useGlobalWebSocket();

    // Локальные реактивные данные для отображения
    const displayStats = ref({
      total_referrals: 0,
      active_referrals: 0,
      referral_balance: '0.00',
      referral_code: '',
      referral_link: '',
      recent_referrals: []
    });

    const displayLink = ref('');

    // Watch для изменений в referralStats из композабла
    watch(referralStats, (newStats) => {
      if (newStats) {
        displayStats.value = { ...newStats };
        lastUpdate.value = new Date().toLocaleTimeString();
        showUpdateIndicator();
      }
    }, { deep: true, immediate: true });

    // Watch для изменений в referralLink из композабла
    watch(referralLink, (newLink) => {
      displayLink.value = newLink;
    }, { immediate: true });

    // Watch для изменений в globalState.referralStats (WebSocket обновления)
    watch(() => globalState.referralStats, (newStats) => {
      if (newStats) {
        displayStats.value = { ...newStats };
        lastUpdate.value = new Date().toLocaleTimeString();
        showUpdateIndicator();
      }
    }, { deep: true });

    // Watch для WebSocket соединения
    watch(connected, (newVal) => {
      if (newVal) {
        loadReferralStats();
      }
    });

    const showUpdateIndicator = () => {
      justUpdated.value = true;
      setTimeout(() => {
        justUpdated.value = false;
      }, 3000);
    };

    const handleCopyReferralLink = () => {
      copyReferralLink();
    };

    onMounted(() => {
      if (connected.value) {
        loadReferralStats();
      } else {
        const interval = setInterval(() => {
          if (connected.value) {
            loadReferralStats();
            clearInterval(interval);
          }
        }, 1000);
        
        setTimeout(() => clearInterval(interval), 10000);
      }
    });

    return {
      displayStats,
      displayLink,
      loading,
      error,
      connected,
      debugInfo,
      justUpdated,
      lastUpdate,
      loadReferralStats,
      copyReferralLink: handleCopyReferralLink
    };
  }
}
</script>

<style scoped>
.debug-info {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  font-size: 12px;
  color: #666;
}

.debug-info p {
  margin: 2px 0;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  color: #c33;
}

.ref-component {
  max-width: 400px;
}

.referral-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  justify-content: space-around;
}

.stat {
  text-align: center;
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #4CAF50;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.referral-link label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.link-container {
  display: flex;
  gap: 8px;
}

.link-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f9f9f9;
}

.copy-btn {
  padding: 8px 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.copy-btn:hover {
  background: #45a049;
}

.referral-hint {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  font-style: italic;
}

.connection-warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
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
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4CAF50;
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


.ref-component h3 {
  color: white;
  margin-bottom: 20px;
}

.referral-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.stat {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-number {
  display: block;
  color: #25438B;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.referral-link label {
  display: block;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.link-container {
  display: flex;
  gap: 10px;
}

.link-input {
  flex: 1;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
}

.copy-btn {
  padding: 10px 15px;
  background: #25438B;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.profile-block {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 25px;
  margin-bottom: 20px;
}
</style>