<template>
  <div class="profile-block balance-block">
    <h3>Баланс</h3>
    
    <div class="balance-amount">
      <span class="amount">{{ balance.amount }}</span>
      <span class="currency">{{ balance.currency }}</span>
    </div>
    
    <div class="balance-actions">
      <button class="action-btn primary" @click="withdraw">Вывести</button>
      <button class="action-btn secondary" @click="deposit">Пополнить</button>
    </div>
    
    <div class="transaction-history">
      <h4>Последние операции</h4>
      <div class="transactions">
        <div v-for="transaction in transactions" :key="transaction.id" class="transaction-item">
          <div class="transaction-info">
            <span class="transaction-desc">{{ transaction.description }}</span>
            <span class="transaction-date">{{ transaction.date }}</span>
          </div>
          <span :class="['transaction-amount', transaction.type]">
            {{ transaction.amount }} {{ balance.currency }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  name: 'BalanceBlock',
  setup() {
    const balance = reactive({
      amount: '1,250.00',
      currency: 'USD'
    });

    const transactions = reactive([
      { id: 1, description: 'Выполнение задания', amount: '+50.00', type: 'income', date: '20.01.2024' },
      { id: 2, description: 'Вывод средств', amount: '-100.00', type: 'outcome', date: '18.01.2024' },
      { id: 3, description: 'Бонус за активность', amount: '+25.00', type: 'income', date: '15.01.2024' }
    ]);

    const withdraw = () => {
      console.log('Withdraw funds');
    };

    const deposit = () => {
      console.log('Deposit funds');
    };

    return {
      balance,
      transactions,
      withdraw,
      deposit
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

.balance-amount {
  text-align: center;
  margin-bottom: 30px;
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

.transaction-history h4 {
  color: white;
  margin-bottom: 15px;
  font-size: 1.1rem;
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
}

.transaction-amount.outcome {
  color: #f44336;
}
</style>