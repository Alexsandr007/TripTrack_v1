import { ref, reactive, computed } from 'vue';

// Глобальное состояние баланса
const balanceState = reactive({
  amount: '0.00',
  currency: 'RUB',
  currency_display: 'Рубли'
});

const transactionsState = ref([]);
const loadingState = ref(false);
const errorState = ref('');

export function useBalance() {
  const formattedAmount = computed(() => {
    const amount = parseFloat(balanceState.amount);
    return isNaN(amount) ? '0,00' : amount.toLocaleString('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  });

  const loadBalanceData = async () => {
    loadingState.value = true;
    errorState.value = '';

    try {
      const token = localStorage.getItem('authToken');
      if (!token) throw new Error('Требуется авторизация');

      const API_BASE = process.env.NODE_ENV === 'development' 
        ? 'http://127.0.0.1:8000' 
        : '';

      const response = await fetch(`${API_BASE}/api/auth/balance-summary/`, {
        method: 'GET',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Ошибка при загрузке данных баланса');

      const data = await response.json();
      
      if (data.success) {
        Object.assign(balanceState, data.balance);
        transactionsState.value = data.transactions;
      } else {
        throw new Error(data.error || 'Ошибка при загрузке данных');
      }
    } catch (err) {
      errorState.value = err.message;
    } finally {
      loadingState.value = false;
    }
  };

  const updateBalance = (newBalance) => {
    Object.assign(balanceState, newBalance);
  };

  const addTransaction = (transaction) => {
    transactionsState.value.unshift(transaction);
    // Ограничиваем количество транзакций
    if (transactionsState.value.length > 10) {
      transactionsState.value = transactionsState.value.slice(0, 10);
    }
  };

  return {
    // Состояние
    balance: balanceState,
    transactions: transactionsState,
    loading: loadingState,
    error: errorState,
    
    // Computed
    formattedAmount,
    
    // Методы
    loadBalanceData,
    updateBalance,
    addTransaction
  };
}