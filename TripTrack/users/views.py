from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
import json

# Импортируем кастомную модель
from users.models import CustomUser
from .serializers import CustomUserRegistrationSerializer, CustomUserSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CustomUserRegistrationAPIView(View):
    """
    API View для регистрации кастомного пользователя
    """
    def post(self, request):
        try:
            print("=== НАЧАЛО РЕГИСТРАЦИИ С КАСТОМНОЙ МОДЕЛЬЮ ===")
            
            # Парсим JSON данные
            body = request.body.decode('utf-8')
            print("Тело запроса:", body)
            data = json.loads(body)
            print("Данные:", data)
            
            # Используем сериализатор для валидации
            serializer = CustomUserRegistrationSerializer(data=data)
            
            if not serializer.is_valid():
                print("Ошибки валидации:", serializer.errors)
                response = JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            
            # Создаем пользователя через сериализатор
            print("Создание кастомного пользователя...")
            user = serializer.save()
            print("Пользователь создан:", user.id, user.username)
            
            # Создаем токен
            token = Token.objects.create(user=user)
            print("Токен создан:", token.key)
            
            # Логиним пользователя
            login(request, user)
            print("Пользователь залогинен")
            
            response_data = {
                'success': True,
                'message': 'Регистрация успешна!',
                'token': token.key,
                'user': CustomUserSerializer(user).data
            }
            print("Ответ:", response_data)
            
            response = JsonResponse(response_data, status=201)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        except json.JSONDecodeError as e:
            print("Ошибка JSON:", str(e))
            response = JsonResponse({
                'success': False,
                'error': 'Неверный формат JSON'
            }, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        except Exception as e:
            print("Общая ошибка:", str(e))
            import traceback
            traceback.print_exc()
            response = JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)
            response["Access-Control-Allow-Origin"] = "*"
            return response

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response


@method_decorator(csrf_exempt, name='dispatch')
class VerifyAuthAPIView(View):
    """
    API View для проверки аутентификации кастомного пользователя
    """
    def get(self, request):
        try:
            from rest_framework.authtoken.models import Token
            
            auth_header = request.headers.get('Authorization', '')
            print("Authorization header:", auth_header)
            
            if not auth_header.startswith('Token '):
                return JsonResponse({
                    'success': False,
                    'error': 'Токен не предоставлен'
                }, status=401)
            
            token = auth_header[6:]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            return JsonResponse({
                'success': True,
                'user': CustomUserSerializer(user).data
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TestAPIView(View):
    """
    Тестовый endpoint для проверки работы API
    """
    def get(self, request):
        from django.conf import settings
        from django.contrib.auth import get_user_model
        
        UserModel = get_user_model()
        user_count = UserModel.objects.count()
        
        return JsonResponse({
            'message': 'API с кастомной моделью работает!',
            'status': 'success',
            'user_model': UserModel.__name__,
            'AUTH_USER_MODEL': getattr(settings, 'AUTH_USER_MODEL', 'Not set'),
            'total_users': user_count
        })