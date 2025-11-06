<template>
  <div class="profile-block balance-block">
    <h3>Баланс</h3>
    
    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>
    
    <!-- Ошибка -->
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="loadBalanceData" class="retry-btn">Повторить</button>
    </div>
    
    <!-- Основной контент -->
    <div v-else>
      <div class="balance-header">
        <div class="balance-amount">
          <span class="amount">{{ formattedAmount }}</span>
          <span class="currency">{{ balance.currency_display || balance.currency }}</span>
        </div>
        <button @click="loadBalanceData" class="refresh-btn" :disabled="loading">
          🔄
        </button>
      </div>
      
      <div class="balance-actions">
        <button class="action-btn primary" @click="withdraw">Вывести</button>
        <button class="action-btn secondary" @click="deposit">Пополнить</button>
      </div>
      
      <div class="transaction-history">
        <div class="transaction-header">
          <h4>Последние операции</h4>
          <button @click="loadBalanceData" class="refresh-btn small" :disabled="loading">
            🔄
          </button>
        </div>
        <div class="transactions">
          <div v-if="transactions.length === 0" class="no-transactions">
            <p>Нет операций</p>
          </div>
          <div v-else v-for="transaction in transactions" :key="transaction.id" class="transaction-item">
            <div class="transaction-info">
              <span class="transaction-desc">{{ transaction.description }}</span>
              <span class="transaction-date">{{ transaction.date }}</span>
            </div>
            <span :class="['transaction-amount', getTransactionType(transaction.type)]">
              {{ transaction.amount_display }} {{ transaction.currency }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useBalance } from '@/composables/useBalance';

export default defineComponent({
  name: 'BalanceBlock',
  setup() {
    const { 
      balance, 
      transactions, 
      formattedAmount, 
      loading, 
      error, 
      loadBalanceData 
    } = useBalance();

    const getTransactionType = (type) => {
      return type === 'income' || type === 'bonus' || type === 'task' ? 'income' : 'outcome';
    };

    onMounted(() => {
      loadBalanceData();
    });

    return {
      balance,
      transactions,
      formattedAmount,
      loading,
      error,
      withdraw: () => console.log('Withdraw'),
      deposit: () => console.log('Deposit'),
      getTransactionType,
      loadBalanceData
    };
  }
});
</script>

<style scoped>
.balance-block h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

/* Стили для загрузки */
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

/* Стили для ошибки */
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

/* Заголовок баланса с кнопкой обновления */
.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.balance-amount {
  text-align: left;
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

/* Заголовок транзакций */
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