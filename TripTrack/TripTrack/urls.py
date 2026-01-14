from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

@csrf_exempt
def test_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'status': 'success', 
                'message': 'Django received your data!',
                'received_data': data
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'message': 'Hello from Django API!', 'method': request.method})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', test_api, name='test_api'),
    path('api/auth/', include('users.urls')),
    # ... другие маршруты
]

# ОБСЛУЖИВАНИЕ СТАТИЧЕСКИХ ФАЙЛОВ ДЛЯ АДМИНКИ
if settings.DEBUG:
    # В режиме разработки
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # В продакшн режиме - ОБЯЗАТЕЛЬНО добавляем статические файлы
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]