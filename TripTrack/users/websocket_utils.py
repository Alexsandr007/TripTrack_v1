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