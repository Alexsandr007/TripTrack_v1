<template>
  <div class="profile-block balance-block">
    <h3>Баланс 
      <span v-if="connected" class="connection-status connected">🟢</span>
      <span v-else class="connection-status disconnected">🔴</span>
    </h3>
    
    <!-- Статус соединения -->
    <!-- <div v-if="!connected" class="connection-warning">
      <p>Нет соединения с сервером. Данные могут быть неактуальны.</p>
      <button @click="loadBalanceData" class="retry-btn">Переподключиться</button>
    </div> -->
    
    <!-- Загрузка -->
    <div v-if="loading && transactions.length === 0" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>
    
    <!-- Ошибка -->
    <div v-else-if="error && transactions.length === 0" class="error-message">
      {{ error }}
      <button @click="loadBalanceData" class="retry-btn">Повторить</button>
    </div>
    
    <!-- Основной контент -->
    <div>
      <div class="balance-header">
        <div class="balance-amount">
          <span class="amount">{{ formattedAmount }}</span>
          <span class="currency">{{ balance.currency_display }}</span>
        </div>
        <div class="balance-controls">
          <span v-if="lastUpdate" class="last-update">
            Обновлено: {{ formatTime(lastUpdate) }}
          </span>
          <!-- <button @click="loadBalanceData" class="refresh-btn" :disabled="loading">
            🔄
          </button> -->
        </div>
      </div>
      
      <div class="balance-actions">
        <button class="action-btn primary" @click="withdraw">Вывести</button>
        <button class="action-btn secondary" @click="deposit">Пополнить</button>
      </div>
      
      <div class="transaction-history">
        <div class="transaction-header">
          <h4>Последние операции</h4>
          <!-- <button @click="loadBalanceData" class="refresh-btn small" :disabled="loading">
            🔄
          </button> -->
        </div>
        
        <!-- Индикатор загрузки новых данных -->
        <div v-if="loading && transactions.length > 0" class="loading-more">
          Обновление данных...
        </div>
        
        <div class="transactions">
          <div v-if="transactions.length === 0" class="no-transactions">
            <p>Нет операций</p>
          </div>
          <div v-else v-for="transaction in transactions" :key="transaction.id" class="transaction-item">
            <div class="transaction-info">
              <span class="transaction-desc">{{ transaction.description }}</span>
              <span class="transaction-date">{{ formatDate(transaction.date) }}</span>
            </div>
            <span :class="['transaction-amount', getTransactionType(transaction.type)]">
              {{ formatTransactionAmount(transaction) }} {{ transaction.currency || balance.currency }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useBalanceWebSocket } from '@/composables/useBalanceWebSocket';

export default defineComponent({
  name: 'BalanceBlock',
  setup() {
    const { 
      balance, 
      transactions, 
      formattedAmount, 
      loading, 
      error,
      connected,
      lastUpdate,
      loadBalanceData,
      withdraw,
      deposit
    } = useBalanceWebSocket();

    const getTransactionType = (type) => {
      const incomeTypes = ['income', 'bonus', 'task', 'deposit', 'refill'];
      return incomeTypes.includes(type) ? 'income' : 'outcome';
    };

    const formatTransactionAmount = (transaction) => {
      const amount = parseFloat(transaction.amount) || 0;
      const sign = getTransactionType(transaction.type) === 'income' ? '+' : '-';
      return `${sign}${Math.abs(amount).toLocaleString('ru-RU', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const formatTime = (date) => {
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    onMounted(() => {
      // Данные автоматически загружаются через WebSocket
      // при подключении в композабле
    });

    return {
      balance,
      transactions,
      formattedAmount,
      loading,
      error,
      connected,
      lastUpdate,
      withdraw,
      deposit,
      getTransactionType,
      formatTransactionAmount,
      formatDate,
      formatTime,
      loadBalanceData
    };
  }
});
</script>

<style scoped>
/* Добавим новые стили для статуса соединения */
.connection-status {
  margin-left: 10px;
  font-size: 0.8rem;
}

.connection-warning {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
  text-align: center;
}

.connection-warning p {
  color: #ffc107;
  margin: 0 0 10px 0;
  font-size: 0.9rem;
}

.balance-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.last-update {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

.loading-more {
  text-align: center;
  padding: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  margin-bottom: 10px;
}

/* Остальные стили остаются такими же, как у вас */
.balance-block h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
}

.loading {
  text-align: center;
  padding: 20px;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #25438B;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.error-message {
  color: #f44336;
  text-align: center;
  padding: 20px;
  background: rgba(244, 67, 54, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #d32f2f;
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(180deg);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn.small {
  padding: 6px;
  font-size: 1rem;
}

.amount {
  color: #25438B;
  font-size: 2.5rem;
  font-weight: bold;
}

.currency {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5rem;
  margin-left: 10px;
}

.balance-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: #25438B;
  color: white;
}

.action-btn.secondary {
  background: transparent;
  border: 2px solid #25438B;
  color: #25438B;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(37, 67, 139, 0.3);
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.transaction-history h4 {
  color: white;
  font-size: 1.1rem;
  margin: 0;
}

.no-transactions {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.5);
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.transaction-info {
  display: flex;
  flex-direction: column;
}

.transaction-desc {
  color: white;
  font-size: 0.9rem;
}

.transaction-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

.transaction-amount.income {
  color: #4CAF50;
  font-weight: 500;
}

.transaction-amount.outcome {
  color: #f44336;
  font-weight: 500;
}
</style>