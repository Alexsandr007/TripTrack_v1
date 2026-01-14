# users/websocket_utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)

def send_balance_update(user_id, new_balance):
    """
    Отправляет обновление баланса через WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "balance_update",
                "balance": str(new_balance)
            }
        )
        print(f"📢 Sent balance update for user {user_id}: {new_balance}")
    except Exception as e:
        logger.error(f"Error sending balance update: {e}")
        print(f"❌ Error sending balance update: {e}")

def send_transaction_update(user_id, transaction_data):
    """
    Отправляет новую транзакцию через WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "transaction_created",
                "transaction": transaction_data
            }
        )
        print(f"📢 Sent transaction update for user {user_id}")
    except Exception as e:
        logger.error(f"Error sending transaction update: {e}")
        print(f"❌ Error sending transaction update: {e}")


def send_referral_update(user_id, referral_data):
    """
    Отправляет обновление реферальной статистики через WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        
        # ✅ ПРАВИЛЬНО: отправляем только обновленные поля в правильном формате
        update_data = {
            'total_referrals': referral_data.get('referral_count', 0),
            'active_referrals': referral_data.get('active_referrals_count', 0),
            'referral_balance': referral_data.get('referral_balance', '0.00'),
            'referral_code': referral_data.get('referral_code', ''),
            'referral_link': referral_data.get('referral_link', ''),
            'recent_referrals': referral_data.get('recent_referrals', [])
        }
        
        # Если есть информация о новом реферале, добавляем ее в recent_referrals
        if 'new_referral' in referral_data:
            update_data['new_referral'] = referral_data['new_referral']
        
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                'type': 'referral_update',
                'referral_data': update_data
            }
        )
        print(f"📊 WebSocket: Отправлено обновление рефералов для user_{user_id}: {update_data}")
    except Exception as e:
        print(f"❌ Ошибка отправки WebSocket рефералов: {e}")


# users/websocket_utils.py
def send_avatar_update(user_id, avatar_url):
    """
    Отправляет обновление аватара через WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                'type': 'avatar_updated',
                'avatar_url': avatar_url
            }
        )
        print(f"🖼️ WebSocket: Отправлено обновление аватара для user_{user_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки WebSocket аватара: {e}")