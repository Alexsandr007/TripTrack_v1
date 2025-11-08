// composables/useGlobalWebSocket.js
import { ref, reactive, onMounted, onUnmounted } from 'vue';

const globalState = reactive({
  user: null,
  balance: '0.00',
  notifications: [],
  onlineUsers: [],
  transactions: [],
  referralStats: null
});

export function useGlobalWebSocket() {
  const connected = ref(false);
  const ws = ref(null);
  const connectionError = ref(null);

  const getWebSocketUrl = () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      console.warn('❌ No auth token found in localStorage');
      return null;
    }

    // Всегда используем порт 8000 для Django в разработке
    const url = `ws://localhost:8000/ws/global/?token=${token}`;
    console.log('🔗 WebSocket URL:', url);
    return url;
  };

  const connect = () => {
    const wsUrl = getWebSocketUrl();
    
    if (!wsUrl) {
      console.error('❌ No auth token found');
      connectionError.value = 'No authentication token';
      return;
    }

    try {
      console.log('🔄 Connecting to WebSocket...');
      
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
        // Переподключаемся через 3 секунды
        setTimeout(connect, 3000);
      };

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      connectionError.value = error.message;
    }
  };

  const handleGlobalMessage = (data) => {
    console.log('🔄 Processing message type:', data.type);
    
    switch (data.type) {
      case 'initial_data':
        console.log('📦 Received initial data');
        if (data.user) globalState.user = data.user;
        if (data.balance) globalState.balance = data.balance;
        if (data.notifications) globalState.notifications = data.notifications;
        if (data.online_users) globalState.onlineUsers = data.online_users;
        if (data.recent_transactions) globalState.transactions = data.recent_transactions;
        if (data.referral_stats) {
          console.log('📊 Received referral stats:', data.referral_stats);
          globalState.referralStats = data.referral_stats;
        }
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
        if (globalState.transactions.length > 20) {
            globalState.transactions = globalState.transactions.slice(0, 20);
        }
        break;
      case 'referral_stats':
        console.log('📊 Referral stats received:', data.stats);
        globalState.referralStats = data.stats;
        break;
      case 'referral_update':
        console.log('📊 Referral update received:', data.referral_data);
        if (globalState.referralStats) {
          globalState.referralStats = {
            ...globalState.referralStats,
            ...data.referral_data
          };
        }
        break;
      default:
        console.log('❓ Unknown message type:', data.type);
    }
  };

  const sendMessage = (type, payload = {}) => {
    if (ws.value && connected.value) {
      const message = JSON.stringify({ type, ...payload });
      console.log('📤 Sending WebSocket message:', message);
      ws.value.send(message);
    } else {
      console.warn('⚠️ Cannot send message - WebSocket not connected');
    }
  };

  onMounted(() => {
    console.log('🏗️ useGlobalWebSocket mounted');
    connect();
  });

  onUnmounted(() => {
    if (ws.value) {
      ws.value.close();
    }
  });

  return {
    globalState,
    connected,
    connectionError,
    sendMessage,
    connect
  };
}