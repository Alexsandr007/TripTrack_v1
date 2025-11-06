# throttling.py
import asyncio
from django.core.cache import cache
from channels.exceptions import DenyConnection

class WebSocketRateThrottle:
    def __init__(self, rate='100/hour'):
        self.num_requests, self.duration = self.parse_rate(rate)
    
    def parse_rate(self, rate):
        num, period = rate.split('/')
        num_requests = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return num_requests, duration
    
    async def allow_connection(self, scope):
        """Проверка лимита подключений"""
        user = scope.get('user')
        if not user or user.is_anonymous:
            return True
        
        cache_key = f"ws_rate_{user.id}"
        count = cache.get(cache_key, 0)
        
        if count >= self.num_requests:
            raise DenyConnection("Rate limit exceeded")
        
        cache.set(cache_key, count + 1, self.duration)
        return True