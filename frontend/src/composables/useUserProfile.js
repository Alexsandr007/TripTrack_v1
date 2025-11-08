// composables/useUserProfile.js
import { ref, computed, onMounted, watch } from 'vue';
import { useGlobalWebSocket } from './useGlobalWebSocket';

export function useUserProfile() {
  const { globalState, connected, sendMessage } = useGlobalWebSocket();
  
  const loading = ref(false);
  const error = ref(null);

  const userProfile = computed(() => {
    return globalState.user || {
      username: '',
      email: '',
      first_name: '',
      full_name: '',
      mentor_login: '',
      date_joined: '',
      referral_code: '',
      balance_amount: '0.00',
      balance_currency: 'USD'
    };
  });

  const formattedRegistrationDate = computed(() => {
    if (!userProfile.value.date_joined) return 'Не указана';
    
    try {
      const date = new Date(userProfile.value.date_joined);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch (e) {
      return userProfile.value.date_joined;
    }
  });

  const loadUserData = () => {
    if (connected.value) {
      loading.value = true;
      error.value = null;
      sendMessage('get_user_data');
      
      setTimeout(() => {
        loading.value = false;
      }, 5000);
    } else {
      error.value = 'Нет соединения с сервером';
    }
  };

  watch(() => globalState.user, (newUser) => {
    console.log('🔄 User profile updated:', newUser);
    loading.value = false;
  }, { deep: true });

  watch(connected, (newVal) => {
    if (newVal) {
      loadUserData();
    }
  });

  onMounted(() => {
    if (connected.value) {
      loadUserData();
    }
  });

  return {
    userProfile,
    formattedRegistrationDate,
    loading,
    error,
    connected,
    loadUserData
  };
}