# TripTrack/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class GlobalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Подключение WebSocket"""
        print("🔌 WebSocket connection attempt...")
        
        # Инициализируем user_group до аутентификации
        self.user_group = None
        self.user = None
        
        self.user = await self.authenticate_user()
        if not self.user or self.user.is_anonymous:
            print("❌ Authentication failed")
            await self.close()
            return

        print(f"✅ User authenticated: {self.user.username}")
        
        # Создаем группу для пользователя
        self.user_group = f"user_{self.user.id}"
        
        # Добавляем в группу
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        print("🌐 WebSocket connection established")
        
        # Отправляем начальные данные
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        """Отключение WebSocket"""
        print(f"🔌 WebSocket disconnected: {close_code}")
        # Удаляем из группы только если она была создана
        if hasattr(self, 'user_group') and self.user_group:
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Обработка входящих сообщений"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            print(f"📨 Received message type: {message_type}")
            
            if message_type == 'get_user_data':
                await self.handle_get_user_data(data)
            elif message_type == 'ping':
                await self.handle_ping(data)
            elif message_type == 'get_referral_stats':
                await self.handle_get_referral_stats(data)
            else:
                print(f"❌ Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
    
    async def handle_get_user_data(self, data):
        """Обработка запроса данных пользователя"""
        user_data = await self.get_user_data()
        await self.send(text_data=json.dumps({
            'type': 'user_data',
            'user': user_data
        }))
    
    async def handle_ping(self, data):
        """Обработка ping-сообщения"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': data.get('timestamp')
        }))
    
    async def handle_get_referral_stats(self, data):
        """Обработка запроса реферальной статистики"""
        print("📊 Handling get_referral_stats request")
        referral_stats = await self.get_referral_stats()
        await self.send(text_data=json.dumps({
            'type': 'referral_stats',
            'stats': referral_stats
        }))
        print("✅ Referral stats sent")

    @database_sync_to_async
    def get_referral_stats(self):
        """Получение реферальной статистики"""
        if not self.user:
            return {}
        
        try:
            # Принудительно генерируем referral_code если его нет
            if not self.user.referral_code:
                self.user.save()  # Это вызовет генерацию кода
                print(f"🔄 Generated referral code for {self.username}: {self.user.referral_code}")
            
            # Получаем базовую статистику
            total_referrals = getattr(self.user, 'referral_count', 0)
            active_referrals = getattr(self.user, 'active_referrals_count', 0)
            referral_balance = str(getattr(self.user, 'referral_balance', '0.00'))
            referral_code = getattr(self.user, 'referral_code', '')
            
            # Генерируем реферальную ссылку
            referral_link = f"http://localhost:8080/register?ref={referral_code}" if referral_code else ""
            
            print(f"📊 Referral stats for {self.user.username}: code={referral_code}, referrals={total_referrals}")
            
            return {
                'total_referrals': total_referrals,
                'active_referrals': active_referrals,
                'referral_balance': referral_balance,
                'referral_code': referral_code,
                'referral_link': referral_link,
                'recent_referrals': []
            }
            
        except Exception as e:
            print(f"❌ Error getting referral stats: {e}")
            return {
                'total_referrals': 0,
                'active_referrals': 0,
                'referral_balance': '0.00',
                'referral_code': '',
                'referral_link': '',
                'recent_referrals': []
            }
    
    async def send_initial_data(self):
        """Отправка начальных данных при подключении"""
        initial_data = {
            'type': 'initial_data',
            'user': await self.get_user_data(),
            'balance': await self.get_user_balance(),
            'notifications': [],
            'online_users': [],
            'recent_transactions': await self.get_recent_transactions(),
            'referral_stats': await self.get_referral_stats(),  # Добавляем реферальную статистику
        }
        
        await self.send(text_data=json.dumps(initial_data))
        print("✅ Initial data sent")
    
    # ===== ОБРАБОТЧИКИ СООБЩЕНИЙ ОТ СЕРВЕРА =====
    
    async def balance_update(self, event):
        """Обработка обновления баланса от сервера"""
        print(f"💰 Received balance update: {event['balance']}")
        await self.send(text_data=json.dumps({
            'type': 'balance_update',
            'balance': event['balance']
        }))
    
    async def transaction_created(self, event):
        """Обработка новой транзакции от сервера"""
        print(f"💳 Received new transaction")
        await self.send(text_data=json.dumps({
            'type': 'transaction_created',
            'transaction': event['transaction']
        }))
    
    async def referral_update(self, event):
        """Обработка обновления реферальной статистики от сервера"""
        print(f"📊 Received referral update: {event['referral_data']}")
        await self.send(text_data=json.dumps({
            'type': 'referral_update',
            'referral_data': event['referral_data']
        }))
    
    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    
    @database_sync_to_async
    def authenticate_user(self):
        """Аутентификация пользователя по токену"""
        try:
            query_string = self.scope.get('query_string', b'').decode()
            token_key = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token_key = param.split('=')[1]
                    break
            
            if not token_key:
                return None
            
            from rest_framework.authtoken.models import Token
            token = Token.objects.get(key=token_key)
            return token.user
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    @database_sync_to_async
    def get_user_data(self):
        """Получение данных пользователя"""
        if not self.user:
            return {}
            
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'balance': str(getattr(self.user, 'balance_amount', '0.00')),
            'balance_currency': getattr(self.user, 'balance_currency', 'USD'),
            'referral_code': getattr(self.user, 'referral_code', ''),
        }
    
    @database_sync_to_async
    def get_user_balance(self):
        return str(getattr(self.user, 'balance_amount', '0.00'))
    
    @database_sync_to_async
    def get_recent_transactions(self):
        """Получение последних транзакций"""
        if not hasattr(self.user, 'transactions'):
            return []
        
        try:
            transactions = self.user.transactions.all().order_by('-created_at')[:5]
            return [{
                'id': t.id,
                'amount': str(t.amount),
                'type': t.transaction_type,
                'description': t.description,
                'date': t.created_at.isoformat()
            } for t in transactions]
        except Exception as e:
            print(f"❌ Error getting transactions: {e}")
            return []
    

    # TripTrack/consumers.py
    @database_sync_to_async
    def get_user_data(self):
        """Получение полных данных пользователя"""
        if not self.user:
            return {}
        
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'full_name': getattr(self.user, 'full_name', ''),
            'mentor_login': getattr(self.user, 'mentor_login', ''),
            'date_joined': self.user.date_joined.isoformat(),
            'last_login': self.user.last_login.isoformat() if self.user.last_login else None,
            'is_active': self.user.is_active,
            'referral_code': getattr(self.user, 'referral_code', ''),
            'balance_amount': str(getattr(self.user, 'balance_amount', '0.00')),
            'balance_currency': getattr(self.user, 'balance_currency', 'USD'),
        }
 