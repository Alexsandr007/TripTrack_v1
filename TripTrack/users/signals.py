# users/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, Transaction
from .websocket_utils import send_balance_update, send_transaction_update

@receiver(post_save, sender=CustomUser)
def user_balance_changed(sender, instance, **kwargs):
    """
    Отправляет обновление баланса при изменении пользователя
    """
    # Проверяем, изменилось ли поле баланса
    if kwargs.get('update_fields') and 'balance_amount' in kwargs['update_fields']:
        print(f"🔄 Balance changed for user {instance.username}: {instance.balance_amount}")
        send_balance_update(instance.id, str(instance.balance_amount))

@receiver(post_save, sender=Transaction)
def transaction_created(sender, instance, created, **kwargs):
    """
    Отправляет уведомление о новой транзакции
    """
    if created:
        print(f"🔄 New transaction for user {instance.user.username}")
        
        # Подготавливаем данные транзакции
        transaction_data = {
            'id': instance.id,
            'amount': str(instance.amount),
            'type': instance.transaction_type,
            'description': instance.description,
            'date': instance.created_at.isoformat()
        }
        
        send_transaction_update(instance.user.id, transaction_data)
        
        # Также отправляем обновление баланса
        send_balance_update(instance.user.id, str(instance.user.balance_amount))

@receiver(post_delete, sender=Transaction)
def transaction_deleted(sender, instance, **kwargs):
    """
    Отправляет обновление баланса при удалении транзакции
    """
    print(f"🔄 Transaction deleted for user {instance.user.username}")
    send_balance_update(instance.user.id, str(instance.user.balance_amount))