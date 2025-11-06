# api/views.py
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer
import json
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_http_methods


# users/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
import json

# Импортируем правильную модель пользователя
from django.conf import settings
if hasattr(settings, 'AUTH_USER_MODEL') and settings.AUTH_USER_MODEL == 'users.CustomUser':
    from .models import CustomUser as User
else:
    from django.contrib.auth.models import User


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_user(request):
    # Обработка preflight CORS запросов
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    if request.method == "POST":
        try:
            # Парсим JSON данные
            data = json.loads(request.body.decode('utf-8'))
            
            # Валидация данных
            errors = {}
            
            if User.objects.filter(username=data.get('login')).exists():
                errors['login'] = ['Пользователь с таким логином уже существует']
                
            if User.objects.filter(email=data.get('email')).exists():
                errors['email'] = ['Пользователь с таким email уже существует']
                
            if data.get('password') != data.get('confirmPassword'):
                errors['password'] = ['Пароли не совпадают']
                
            if errors:
                response = JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            
            # Создаем пользователя
            user = User.objects.create_user(
                username=data.get('login'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('fullName')
            )
            
            # Создаем токен для пользователя
            token, created = Token.objects.get_or_create(user=user)
            
            # Логиним пользователя
            login(request, user)
            
            response = JsonResponse({
                'success': True,
                'message': 'Регистрация успешна!',
                'token': token.key,  # Добавляем токен в ответ
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'fullName': user.first_name
                }
            }, status=201)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        except json.JSONDecodeError:
            response = JsonResponse({
                'success': False,
                'error': 'Неверный формат JSON'
            }, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        except Exception as e:
            response = JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
            response["Access-Control-Allow-Origin"] = "*"
            return response
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_auth(request):
    return Response({
        'success': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'fullName': request.user.first_name,
        }
    })

# И простой endpoint для проверки токена
@csrf_exempt
def check_token(request):
    if request.method == 'GET':
        # Проверяем токен из заголовков
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            token = auth_header[6:]
            try:
                from rest_framework.authtoken.models import Token
                token_obj = Token.objects.get(key=token)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': token_obj.user.id,
                        'username': token_obj.user.username,
                        'email': token_obj.user.email,
                        'fullName': token_obj.user.first_name,
                    }
                })
            except Token.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid token'}, status=401)
        return JsonResponse({'success': False, 'error': 'No token provided'}, status=401)