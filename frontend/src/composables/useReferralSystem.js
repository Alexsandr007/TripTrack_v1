// composables/useReferralSystem.js
import { ref, computed, onMounted, watch } from 'vue';
import { useGlobalWebSocket } from './useGlobalWebSocket';

export function useReferralSystem() {
  const { globalState, connected, sendMessage } = useGlobalWebSocket();
  
  const loading = ref(false);
  const error = ref(null);

  // Реактивная ссылка на данные из globalState
  const referralStats = computed(() => {
    const stats = globalState.referralStats || {
      total_referrals: 0,
      active_referrals: 0,
      referral_balance: '0.00',
      referral_code: '',
      referral_link: '',
      recent_referrals: []
    };
    
    console.log('📊 referralStats computed returned:', stats);
    return stats;
  });

  const referralLink = computed(() => {
    const stats = referralStats.value;
    const link = stats.referral_link;
    
    if (link) {
      console.log('🔗 Using backend referral link:', link);
      return link;
    }
    
    // Генерация ссылки на фронтенде, если нет с бэкенда
    const code = stats.referral_code;
    if (code) {
      const generatedLink = `${window.location.origin}/register?ref=${code}`;
      console.log('🔗 Generated referral link:', generatedLink);
      return generatedLink;
    }
    
    console.log('❌ No referral code available');
    return '';
  });

  const loadReferralStats = () => {
    console.log('🔄 Loading referral stats, connected:', connected.value);
    if (connected.value) {
      loading.value = true;
      error.value = null;
      console.log('📤 Sending get_referral_stats message');
      sendMessage('get_referral_stats');
      
      // Сбрасываем loading через 5 секунд
      setTimeout(() => {
        if (loading.value) {
          loading.value = false;
          console.log('⏰ Loading timeout');
        }
      }, 5000);
    } else {
      console.warn('⚠️ WebSocket not connected');
      error.value = 'WebSocket не подключен';
    }
  };

  const copyReferralLink = async () => {
    const link = referralLink.value;
    if (!link) {
      alert('Реферальная ссылка недоступна');
      return;
    }

    try {
      await navigator.clipboard.writeText(link);
      alert('Реферальная ссылка скопирована!');
    } catch (err) {
      console.error('Ошибка копирования:', err);
      // Fallback для старых браузеров
      const textArea = document.createElement('textarea');
      textArea.value = link;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Реферальная ссылка скопирована!');
    }
  };

  // Следим за изменениями в globalState
  watch(() => globalState.referralStats, (newStats) => {
    console.log('🔄 useReferralSystem: globalState.referralStats updated', newStats);
    loading.value = false;
  }, { deep: true });

  onMounted(() => {
    console.log('🏗️ useReferralSystem mounted');
    if (connected.value) {
      loadReferralStats();
    }
  });

  return {
    referralStats,
    referralLink,
    loading,
    error,
    loadReferralStats,
    copyReferralLink
  };
}