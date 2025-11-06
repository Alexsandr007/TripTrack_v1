// composables/useGlobalWebSocket.js
import { ref, reactive, onMounted, onUnmounted } from 'vue';

const globalState = reactive({
  user: null,
  balance: '0.00',
  notifications: [],
  onlineUsers: [],
  transactions: []
});

export function useGlobalWebSocket() {
  const connected = ref(false);
  const ws = ref(null);
  const connectionError = ref(null);

  const getWebSocketUrl = () => {
    const token = localStorage.getItem('authToken');
    if (!token) return null;

    // Всегда используем порт 8000 для Django в разработке
    return `ws://localhost:8000/ws/global/?token=${token}`;
  };

  const connect = () => {
    const wsUrl = getWebSocketUrl();
    
    if (!wsUrl) {
      console.error('❌ No auth token found');
      connectionError.value = 'No authentication token';
      return;
    }

    try {
      console.log('🔄 Connecting to WebSocket:', wsUrl);
      
      ws.value = new WebSocket(wsUrl);

      ws.value.onopen = () => {
        connected.value = true;
        connectionError.value = null;
        console.log('🌐 Global WebSocket connected');
      };

      ws.value.onmessage = (event) => {
        console.log('📨 WebSocket message received:', event.data);
        try {
          const data = JSON.parse(event.data);
          handleGlobalMessage(data);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.value.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        connectionError.value = 'WebSocket connection error';
      };

      ws.value.onclose = () => {
        connected.value = false;
        console.log('🔌 WebSocket closed');
        setTimeout(connect, 5000);
      };

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      connectionError.value = error.message;
    }
  };

  const handleGlobalMessage = (data) => {
    switch (data.type) {
      case 'initial_data':
        if (data.user) globalState.user = data.user;
        if (data.balance) globalState.balance = data.balance;
        if (data.notifications) globalState.notifications = data.notifications;
        if (data.online_users) globalState.onlineUsers = data.online_users;
        if (data.recent_transactions) globalState.transactions = data.recent_transactions;
        break;
      case 'user_data':
        if (data.user) globalState.user = data.user;
        break;
      case 'balance_update':
        console.log('💰 Balance update received:', data.balance);
        globalState.balance = data.balance;
        if (globalState.user) {
            globalState.user.balance = data.balance;
        }
        break;
        
      case 'transaction_created':
        console.log('💳 New transaction received:', data.transaction);
        globalState.transactions.unshift(data.transaction);
        // Ограничиваем количество транзакций
        if (globalState.transactions.length > 20) {
            globalState.transactions = globalState.transactions.slice(0, 20);
        }
        break;
    }
  };

  const sendMessage = (type, payload = {}) => {
    if (ws.value && connected.value) {
      ws.value.send(JSON.stringify({ type, ...payload }));
    }
  };

  onMounted(connect);
  onUnmounted(() => ws.value?.close());

  return {
    globalState,
    connected,
    connectionError,
    sendMessage
  };
}