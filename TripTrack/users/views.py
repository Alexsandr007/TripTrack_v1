from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
import json

# Импортируем кастомную модель
from users.models import CustomUser, Transaction
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
            
            # Дополнительные проверки перед сериализатором
            errors = {}
            
            # Проверка логина (без учета регистра)
            login = data.get('login', '').strip()
            if login:
                login_lower = login.lower()
                print(f"Проверка уникальности логина: {login} (нижний регистр: {login_lower})")
                
                if CustomUser.objects.filter(username__iexact=login_lower).exists():
                    existing_user = CustomUser.objects.filter(username__iexact=login_lower).first()
                    print(f"Логин {login} уже существует (регистр не учитывается). Существующий: {existing_user.username}")
                    errors['login'] = [f'Пользователь с логином "{login}" уже существует (регистр не учитывается)']
            
            # Проверка email (без учета регистра)
            email = data.get('email', '').strip()
            if email:
                email_lower = email.lower()
                print(f"Проверка уникальности email: {email} (нижний регистр: {email_lower})")
                
                if CustomUser.objects.filter(email__iexact=email_lower).exists():
                    existing_user = CustomUser.objects.filter(email__iexact=email_lower).first()
                    print(f"Email {email} уже существует (регистр не учитывается). Существующий: {existing_user.email}")
                    errors['email'] = [f'Пользователь с email "{email}" уже существует (регистр не учитывается)']
            
            # Проверка ментора (без учета регистра)
            mentor_login = data.get('Mentorlogin', '').strip()
            if mentor_login:
                mentor_login_lower = mentor_login.lower()
                print(f"Проверка существования ментора: {mentor_login} (нижний регистр: {mentor_login_lower})")
                
                if not CustomUser.objects.filter(username__iexact=mentor_login_lower).exists():
                    print(f"Ментор с логином {mentor_login} не найден (регистр не учитывается)")
                    errors['Mentorlogin'] = [f'Ментор с логином "{mentor_login}" не существует']
                else:
                    mentor = CustomUser.objects.get(username__iexact=mentor_login_lower)
                    print(f"Ментор {mentor_login} найден в базе (фактический логин: {mentor.username})")
            
            # Если есть ошибки на этом этапе, возвращаем их
            if errors:
                print("Ошибки предварительной проверки:", errors)
                response = JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            
            # Используем сериализатор для валидации
            serializer = CustomUserRegistrationSerializer(data=data)
            
            if not serializer.is_valid():
                print("Ошибки валидации сериализатора:", serializer.errors)
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
    
@method_decorator(csrf_exempt, name='dispatch')
class CustomUserLoginAPIView(View):
    """
    API View для авторизации кастомного пользователя
    """
    def post(self, request):
        try:
            print("=== НАЧАЛО АВТОРИЗАЦИИ ===")
            
            # Парсим JSON данные
            body = request.body.decode('utf-8')
            print("Тело запроса:", body)
            data = json.loads(body)
            print("Данные авторизации:", data)
            
            # Валидация обязательных полей
            errors = {}
            username = data.get('login', '').strip()
            password = data.get('password', '').strip()
            
            if not username:
                errors['login'] = ['Логин обязателен']
            if not password:
                errors['password'] = ['Пароль обязателен']
            
            if errors:
                print("Ошибки валидации:", errors)
                response = JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            
            # Аутентификация пользователя
            print(f"Аутентификация пользователя: {username}")
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Пользователь аутентифицирован
                print(f"Пользователь аутентифицирован: {user.username}")
                
                # Логиним пользователя
                login(request, user)
                print("Пользователь залогинен")
                
                # Получаем или создаем токен
                token, created = Token.objects.get_or_create(user=user)
                print("Токен:", token.key)
                
                response_data = {
                    'success': True,
                    'message': 'Авторизация успешна!',
                    'token': token.key,
                    'user': CustomUserSerializer(user).data
                }
                print("Успешный ответ:", response_data)
                
                response = JsonResponse(response_data, status=200)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            else:
                # Неверные учетные данные
                print("Неверные учетные данные")
                response = JsonResponse({
                    'success': False,
                    'error': 'Неверный логин или пароль'
                }, status=401)
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
            print("Общая ошибка авторизации:", str(e))
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
class CustomUserLogoutAPIView(View):
    """
    API View для выхода кастомного пользователя
    """
    def post(self, request):
        try:
            print("=== НАЧАЛО ВЫХОДА ИЗ СИСТЕМЫ ===")
            
            # Получаем токен из заголовков
            auth_header = request.headers.get('Authorization', '')
            print("Authorization header:", auth_header)
            
            if auth_header.startswith('Token '):
                token = auth_header[6:]
                try:
                    # Находим и удаляем токен
                    token_obj = Token.objects.get(key=token)
                    user = token_obj.user
                    print(f"Выход пользователя: {user.username}")
                    
                    # Удаляем токен
                    token_obj.delete()
                    print("Токен удален")
                    
                    # Выход из системы
                    from django.contrib.auth import logout
                    logout(request)
                    print("Пользователь разлогинен")
                    
                    response_data = {
                        'success': True,
                        'message': 'Выход выполнен успешно'
                    }
                    
                    response = JsonResponse(response_data, status=200)
                    response["Access-Control-Allow-Origin"] = "*"
                    return response
                    
                except Token.DoesNotExist:
                    print("Токен не найден, но все равно возвращаем успех")
                    # Даже если токен не найден, считаем что выход выполнен
                    response = JsonResponse({
                        'success': True,
                        'message': 'Выход выполнен'
                    }, status=200)
                    response["Access-Control-Allow-Origin"] = "*"
                    return response
            
            # Если нет токена, все равно считаем выход успешным
            print("Токен не предоставлен, но выход выполнен")
            response = JsonResponse({
                'success': True,
                'message': 'Выход выполнен'
            }, status=200)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        except Exception as e:
            print("Ошибка при выходе:", str(e))
            import traceback
            traceback.print_exc()
            # Даже при ошибке возвращаем успех для клиента
            response = JsonResponse({
                'success': True,
                'message': 'Выход выполнен'
            }, status=200)
            response["Access-Control-Allow-Origin"] = "*"
            return response

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    

@method_decorator(csrf_exempt, name='dispatch')
class UserBalanceAPIView(View):
    """
    API View для получения баланса пользователя
    """
    def get(self, request):
        try:
            print("=== ПОЛУЧЕНИЕ БАЛАНСА ПОЛЬЗОВАТЕЛЯ ===")
            
            # Получаем токен из заголовков
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Token '):
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация'
                }, status=401)
            
            token = auth_header[6:]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            print(f"Получение баланса для пользователя: {user.username}")
            
            # Баланс уже в модели пользователя, просто сериализуем
            balance_data = {
                'amount': str(user.balance_amount),
                'currency': user.balance_currency,
                'currency_display': user.get_balance_currency_display(),
                'updated_at': user.balance_updated_at.strftime('%d.%m.%Y %H:%M')
            }
            
            print(f"Баланс пользователя {user.username}: {user.balance_amount} {user.balance_currency}")
            
            return JsonResponse({
                'success': True,
                'balance': balance_data
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при получении баланса:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserTransactionsAPIView(View):
    """
    API View для получения транзакций пользователя
    """
    def get(self, request):
        try:
            print("=== ПОЛУЧЕНИЕ ТРАНЗАКЦИЙ ПОЛЬЗОВАТЕЛЯ ===")
            
            # Получаем токен из заголовков
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Token '):
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация'
                }, status=401)
            
            token = auth_header[6:]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            # Получаем параметр limit из запроса (по умолчанию 3)
            limit = int(request.GET.get('limit', 3))
            
            print(f"Получение {limit} транзакций для пользователя: {user.username}")
            
            # Получаем последние транзакции
            transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:limit]
            
            # Сериализуем данные транзакций
            transactions_data = []
            for transaction in transactions:
                transaction_data = {
                    'id': transaction.id,
                    'amount': str(transaction.amount),
                    'amount_display': f"+{transaction.amount}" if transaction.transaction_type in ['income', 'bonus', 'task'] else f"-{transaction.amount}",
                    'currency': transaction.currency,
                    'transaction_type': transaction.transaction_type,
                    'type_display': transaction.get_transaction_type_display(),
                    'description': transaction.description,
                    'status': transaction.status,
                    'date': transaction.created_at.strftime('%d.%m.%Y')
                }
                transactions_data.append(transaction_data)
            
            print(f"Найдено {len(transactions_data)} транзакций для пользователя {user.username}")
            
            return JsonResponse({
                'success': True,
                'transactions': transactions_data,
                'total_count': len(transactions_data)
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при получении транзакций:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserBalanceSummaryAPIView(View):
    """
    API View для получения сводной информации о балансе и транзакциях
    """
    def get(self, request):
        try:
            print("=== ПОЛУЧЕНИЕ СВОДНОЙ ИНФОРМАЦИИ О БАЛАНСЕ ===")
            
            # Получаем токен из заголовков
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Token '):
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация'
                }, status=401)
            
            token = auth_header[6:]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            print(f"Получение сводной информации для пользователя: {user.username}")
            
            # Получаем последние 3 транзакции
            transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:3]
            
            # Формируем данные баланса (теперь из полей пользователя)
            balance_data = {
                'amount': str(user.balance_amount),
                'currency': user.balance_currency,
                'currency_display': user.get_balance_currency_display(),
                'updated_at': user.balance_updated_at.strftime('%d.%m.%Y %H:%M')
            }
            
            # Формируем данные транзакций
            transactions_data = []
            for transaction in transactions:
                transaction_data = {
                    'id': transaction.id,
                    'amount': str(transaction.amount),
                    'amount_display': f"+{transaction.amount}" if transaction.transaction_type in ['income', 'bonus', 'task'] else f"-{transaction.amount}",
                    'currency': transaction.currency,
                    'type': transaction.transaction_type,
                    'type_display': transaction.get_transaction_type_display(),
                    'description': transaction.description,
                    'date': transaction.created_at.strftime('%d.%m.%Y')
                }
                transactions_data.append(transaction_data)
            
            print(f"Сводная информация: баланс {user.balance_amount} {user.balance_currency}, {len(transactions_data)} транзакций")
            
            return JsonResponse({
                'success': True,
                'balance': balance_data,
                'transactions': transactions_data
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при получении сводной информации:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)