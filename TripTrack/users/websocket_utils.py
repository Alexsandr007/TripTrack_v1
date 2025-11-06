# users/websocket_utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_balance_update(user_id, new_balance):
    """
    Отправляет обновление баланса через WebSocket
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "balance_update",
            "balance": str(new_balance)
        }
    )
    print(f"📢 Sent balance update for user {user_id}: {new_balance}")

def send_transaction_update(user_id, transaction_data):
    """
    Отправляет новую транзакцию через WebSocket
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "transaction_created",
            "transaction": transaction_data
        }
    )
    print(f"📢 Sent transaction update for user {user_id}")