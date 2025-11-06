from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
    path('api/auth/', include('users.urls')),  # Замените 'your_app' на имя вашего DRF приложения
    # ... другие маршруты
]

