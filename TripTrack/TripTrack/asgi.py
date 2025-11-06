# TripTrack/asgi.py
import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TripTrack.settings')

# Инициализируем Django
django_application = get_asgi_application()

# Настраиваем WebSocket
try:
    django.setup()
    
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    
    # Импортируем WebSocket routing
    try:
        from TripTrack.routing import websocket_urlpatterns
        
        application = ProtocolTypeRouter({
            "http": django_application,
            "websocket": AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            ),
        })
        print("✅ ASGI with WebSocket configured successfully")
        
    except ImportError as e:
        print(f"❌ Could not import WebSocket routing: {e}")
        application = django_application
        
except Exception as e:
    print(f"❌ WebSocket setup failed: {e}")
    application = django_application