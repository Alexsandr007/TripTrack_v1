// composables/useBalanceWebSocket.js
import { ref, computed, onMounted, watch } from 'vue';
import { useGlobalWebSocket } from './useGlobalWebSocket';

export function useBalanceWebSocket() {
  const { globalState, connected, connectionError, sendMessage, connect } = useGlobalWebSocket();
  
  const loading = ref(false);
  const error = ref(null);
  const lastUpdate = ref(null);

  // Автоматически загружаем данные при подключении
  watch(connected, (newVal) => {
    if (newVal) {
      console.log('🔄 WebSocket connected, loading balance data...');
      loadBalanceData();
    } else {
      error.value = connectionError.value || 'Нет соединения с сервером';
    }
  });

  // Реактивные данные из глобального состояния
  const balance = computed(() => ({
    amount: globalState.balance || '0.00',
    currency: globalState.user?.balance_currency || 'USD',
    currency_display: globalState.user?.balance_currency || 'USD'
  }));

  const transactions = computed(() => 
    globalState.transactions || []
  );

  const formattedAmount = computed(() => {
    const amount = parseFloat(balance.value.amount) || 0;
    return amount.toLocaleString('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  });

  const loadBalanceData = () => {
    if (connected.value) {
      loading.value = true;
      error.value = null;
      console.log('📨 Requesting user data via WebSocket...');
      sendMessage('get_user_data');
      
      setTimeout(() => {
        if (loading.value) {
          loading.value = false;
          if (!connected.value) {
            error.value = 'Нет соединения с сервером';
          }
        }
      }, 5000);
    } else {
      error.value = 'Нет соединения с сервером';
      console.log('🔄 Attempting to reconnect WebSocket...');
      connect(); // Пытаемся переподключиться
    }
  };

  const withdraw = () => {
    if (connected.value) {
      sendMessage('create_transaction', {
        transaction: {
          amount: '-100.00',
          type: 'withdrawal',
          description: 'Вывод средств'
        }
      });
    } else {
      error.value = 'Нет соединения для выполнения операции';
    }
  };

  const deposit = () => {
    if (connected.value) {
      sendMessage('create_transaction', {
        transaction: {
          amount: '100.00',
          type: 'deposit',
          description: 'Пополнение счета'
        }
      });
    } else {
      error.value = 'Нет соединения для выполнения операции';
    }
  };

  onMounted(() => {
    // Если уже подключены, загружаем данные
    if (connected.value) {
      loadBalanceData();
    } else {
      // Иначе показываем сообщение о подключении
      error.value = 'Устанавливается соединение...';
    }
  });

  return {
    balance,
    transactions,
    formattedAmount,
    loading,
    error,
    connected,
    lastUpdate,
    loadBalanceData,
    withdraw,
    deposit,
    reconnect: connect
  };
}