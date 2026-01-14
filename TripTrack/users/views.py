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
from .websocket_utils import send_referral_update

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

            # Обработка реферального кода
            referral_code = data.get('referral_code', '').strip()
            referring_user = None
            if referral_code:
                print(f"Обработка реферального кода: {referral_code}")
                try:
                    referring_user = CustomUser.objects.get(referral_code=referral_code)
                    print(f"Найден реферер: {referring_user.username}")
                    # Сохраняем объект реферера для передачи в сериализатор
                    data['referring_user'] = referring_user
                except CustomUser.DoesNotExist:
                    print(f"Реферальный код не найден: {referral_code}")
                    # Не прерываем регистрацию, просто игнорируем неверный код
            
            # Дополнительные проверки перед сериализатором
            errors = {}
            
            # Проверка логина (без учета регистра)
            username = data.get('login', '').strip()
            if username:
                login_lower = username.lower()
                print(f"Проверка уникальности логина: {username} (нижний регистр: {login_lower})")
                
                if CustomUser.objects.filter(username__iexact=login_lower).exists():
                    existing_user = CustomUser.objects.filter(username__iexact=login_lower).first()
                    print(f"Логин {username} уже существует (регистр не учитывается). Существующий: {existing_user.username}")
                    errors['login'] = [f'Пользователь с логином "{username}" уже существует (регистр не учитывается)']
            
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
            
            # ОБРАБОТКА РЕФЕРАЛЬНОЙ СИСТЕМЫ ПОСЛЕ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ
            if referring_user:
                try:
                    # Обновляем счетчик рефералов у реферера
                    referring_user.refresh_from_db()
                    referring_user.referral_count = referring_user.referrals.count()
                    referring_user.save()
                    
                    print(f"✅ Реферал зарегистрирован: {user.username} -> {referring_user.username}")
                    print(f"📊 Новое количество рефералов у {referring_user.username}: {referring_user.referral_count}")
                    
                    # Отправляем WebSocket уведомление рефереру

                    send_referral_update(referring_user.id, {
                        'referral_count': referring_user.referral_count,  # Это станет total_referrals
                        'active_referrals_count': referring_user.active_referrals_count,  # Это станет active_referrals
                        'referral_balance': str(referring_user.referral_balance),
                        'referral_code': referring_user.referral_code,
                        'referral_link': f"http://localhost:8080/register?ref={referring_user.referral_code}",
                        'new_referral': {
                            'username': user.username,
                            'full_name': user.full_name,
                            'registration_date': user.date_joined.isoformat()
                        }
                    })
                    print(f"📨 WebSocket уведомление отправлено рефереру {referring_user.username}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при обработке реферальной системы: {e}")
                    # Не прерываем регистрацию из-за ошибки реферальной системы
            
            # Создаем токен
            token = Token.objects.create(user=user)
            print("Токен создан:", token.key)
            
            # Логиним пользователя
            login(request, user)
            print("Пользователь залогинен")
            
            # Формируем ответ с информацией о реферале
            response_data = {
                'success': True,
                'message': 'Регистрация успешна!',
                'token': token.key,
                'user': CustomUserSerializer(user).data
            }
            
            # Добавляем информацию о реферале в ответ, если есть
            if referring_user:
                response_data['referral_info'] = {
                    'referred_by': referring_user.username,
                    'referral_code_used': referral_code
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


# Добавьте новый endpoint для реферальной статистики
@method_decorator(csrf_exempt, name='dispatch')
class ReferralStatsAPIView(View):
    def get(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Token '):
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация'
                }, status=401)
            
            token = auth_header[6:]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            stats = {
                'total_referrals': user.referral_count,
                'active_referrals': user.active_referrals_count,
                'referral_balance': str(user.referral_balance),
                'referral_code': user.referral_code,
                'referral_link': f"https://t.me/yourbot?start=ref{user.referral_code}"
            }
            
            return JsonResponse({
                'success': True,
                'stats': stats
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
        

# Добавьте в конец views.py

@method_decorator(csrf_exempt, name='dispatch')
class UpdateBalanceAPIView(View):
    """
    API View для обновления баланса пользователя с WebSocket уведомлением
    """
    def post(self, request):
        try:
            print("=== ОБНОВЛЕНИЕ БАЛАНСА ===")
            
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
            
            # Парсим данные
            data = json.loads(request.body.decode('utf-8'))
            new_balance = data.get('balance')
            
            if not new_balance:
                return JsonResponse({
                    'success': False,
                    'error': 'Баланс не указан'
                }, status=400)
            
            print(f"Обновление баланса для {user.username}: {user.balance_amount} -> {new_balance}")
            
            # Обновляем баланс
            from decimal import Decimal
            user.balance_amount = Decimal(new_balance)
            user.save()
            
            # Отправляем WebSocket уведомление
            from .websocket_utils import send_balance_update
            send_balance_update(user.id, new_balance)
            
            return JsonResponse({
                'success': True,
                'message': 'Баланс обновлен',
                'new_balance': str(new_balance)
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при обновлении баланса:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


@method_decorator(csrf_exempt, name='dispatch')
class CreateTransactionAPIView(View):
    """
    API View для создания транзакции с WebSocket уведомлением
    """
    def post(self, request):
        try:
            print("=== СОЗДАНИЕ ТРАНЗАКЦИИ ===")
            
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
            
            # Парсим данные
            data = json.loads(request.body.decode('utf-8'))
            amount = data.get('amount')
            transaction_type = data.get('type', 'income')
            description = data.get('description', '')
            
            if not amount:
                return JsonResponse({
                    'success': False,
                    'error': 'Сумма не указана'
                }, status=400)
            
            print(f"Создание транзакции для {user.username}: {amount} {transaction_type}")
            
            # Создаем транзакцию
            from decimal import Decimal
            transaction = Transaction.objects.create(
                user=user,
                amount=Decimal(amount),
                transaction_type=transaction_type,
                description=description,
                currency=user.balance_currency
            )
            
            # Обновляем баланс пользователя
            if transaction_type in ['income', 'bonus', 'task']:
                user.balance_amount += Decimal(amount)
            else:
                user.balance_amount -= Decimal(amount)
            user.save()
            
            # Подготавливаем данные для WebSocket
            transaction_data = {
                'id': transaction.id,
                'amount': str(transaction.amount),
                'type': transaction.transaction_type,
                'description': transaction.description,
                'date': transaction.created_at.isoformat()
            }
            
            # Отправляем WebSocket уведомления
            from .websocket_utils import send_balance_update, send_transaction_update
            send_balance_update(user.id, user.balance_amount)
            send_transaction_update(user.id, transaction_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Транзакция создана',
                'transaction': transaction_data,
                'new_balance': str(user.balance_amount)
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при создании транзакции:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    

# Добавьте после существующих классов в users/views.py

@method_decorator(csrf_exempt, name='dispatch')
class ReferralStatsAPIView(View):
    """
    API View для получения реферальной статистики
    """
    def get(self, request):
        try:
            print("=== ПОЛУЧЕНИЕ РЕФЕРАЛЬНОЙ СТАТИСТИКИ ===")
            
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
            
            print(f"Получение реферальной статистики для пользователя: {user.username}")
            
            # Получаем базовую статистику
            total_referrals = getattr(user, 'referral_count', 0)
            active_referrals = getattr(user, 'active_referrals_count', 0)
            referral_balance = str(getattr(user, 'referral_balance', '0.00'))
            referral_code = getattr(user, 'referral_code', '')
            
            # Генерируем реферальную ссылку
            referral_link = f"https://t.me/yourbot?start=ref{referral_code}" if referral_code else ""
            
            # Получаем информацию о последних рефералах
            recent_referrals = []
            if hasattr(user, 'referrals'):
                referrals = user.referrals.all().order_by('-date_joined')[:5]
                recent_referrals = [{
                    'username': ref.username,
                    'full_name': ref.full_name or ref.first_name or ref.username,
                    'email': ref.email,
                    'registration_date': ref.date_joined.isoformat(),
                    'is_active': ref.is_active
                } for ref in referrals]
            
            stats = {
                'total_referrals': total_referrals,
                'active_referrals': active_referrals,
                'referral_balance': referral_balance,
                'referral_code': referral_code,
                'referral_link': referral_link,
                'recent_referrals': recent_referrals
            }
            
            print(f"Реферальная статистика для {user.username}: {total_referrals} рефералов")
            
            return JsonResponse({
                'success': True,
                'stats': stats
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при получении реферальной статистики:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


@method_decorator(csrf_exempt, name='dispatch')
class ReferralLinkAPIView(View):
    """
    API View для получения реферальной ссылки
    """
    def get(self, request):
        try:
            print("=== ПОЛУЧЕНИЕ РЕФЕРАЛЬНОЙ ССЫЛКИ ===")
            
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
            
            print(f"Получение реферальной ссылки для пользователя: {user.username}")
            
            referral_code = getattr(user, 'referral_code', '')
            if not referral_code:
                # Генерируем код, если его нет
                user.save()  # Это вызовет генерацию кода в методе save()
                referral_code = user.referral_code
            
            # Генерируем реферальную ссылку
            referral_link = f"https://t.me/yourbot?start=ref{referral_code}"
            
            print(f"Реферальная ссылка для {user.username}: {referral_link}")
            
            return JsonResponse({
                'success': True,
                'referral_link': referral_link,
                'referral_code': referral_code
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при получении реферальной ссылки:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


# users/views.py
@method_decorator(csrf_exempt, name='dispatch')
class GetMentorByReferralCodeView(View):
    """
    API для получения информации о менторе по реферальному коду
    """
    def get(self, request):
        try:
            ref_code = request.GET.get('ref', '').strip()
            print(f"🔍 GetMentorByReferralCodeView: received ref_code = '{ref_code}'")
            
            if not ref_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Реферальный код не указан'
                }, status=400)
            
            try:
                mentor = CustomUser.objects.get(referral_code=ref_code)
                print(f"✅ Найден ментор: {mentor.username} с кодом {ref_code}")
                
                return JsonResponse({
                    'success': True,
                    'mentor': {
                        'login': mentor.username,
                        'full_name': mentor.full_name or mentor.first_name or mentor.username,
                        'email': mentor.email
                    }
                })
            except CustomUser.DoesNotExist:
                print(f"❌ Ментор с кодом {ref_code} не найден")
                return JsonResponse({
                    'success': False,
                    'error': 'Реферальный код не найден'
                }, status=404)
                
        except Exception as e:
            print(f"❌ Ошибка в GetMentorByReferralCodeView: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# users/views.py
import os
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

@method_decorator(csrf_exempt, name='dispatch')
class UpdateAvatarAPIView(View):
    """
    API View для обновления аватара пользователя
    """
    def post(self, request):
        try:
            print("=== ОБНОВЛЕНИЕ АВАТАРА ===")
            
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
            
            # Проверяем наличие файла
            if 'avatar' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'Файл аватара не предоставлен'
                }, status=400)
            
            avatar_file = request.FILES['avatar']
            
            # Валидация файла
            if avatar_file.size > 5 * 1024 * 1024:  # 5MB
                return JsonResponse({
                    'success': False,
                    'error': 'Файл слишком большой. Максимальный размер: 5MB'
                }, status=400)
            
            if not avatar_file.content_type.startswith('image/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Файл должен быть изображением'
                }, status=400)
            
            # Сохраняем аватар
            user.avatar = avatar_file
            user.save()
            
            # ДИАГНОСТИКА
            print(f"📁 Абсолютный путь: {user.avatar.path}")
            print(f"🌐 URL: {user.avatar.url}")
            print(f"✅ Файл существует: {os.path.exists(user.avatar.path)}")
            
            # Получаем URL аватара
            avatar_url = user.avatar.url
            
            print(f"✅ Аватар обновлен для пользователя {user.username}")
            
            # Отправляем WebSocket уведомление
            try:
                from .websocket_utils import send_avatar_update
                send_avatar_update(user.id, avatar_url)
            except Exception as ws_error:
                print(f"⚠️ WebSocket ошибка: {ws_error}")
            
            return JsonResponse({
                'success': True,
                'message': 'Аватар успешно обновлен',
                'avatar_url': avatar_url  # Относительный путь
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("❌ Ошибка при обновлении аватара:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

    def options(self, request, *args, **kwargs):
        """Обработка CORS preflight"""
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    


# users/views.py
@method_decorator(csrf_exempt, name='dispatch')
class SaveTelegramAPIView(View):
    """
    API View для сохранения Telegram ссылки
    """
    def post(self, request):
        try:
            print("=== СОХРАНЕНИЕ TELEGRAM ===")
            
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
            
            # Проверяем данные
            data = json.loads(request.body)
            telegram_link = data.get('telegram_link', '').strip()
            
            if not telegram_link:
                return JsonResponse({
                    'success': False,
                    'error': 'Ссылка на Telegram обязательна'
                }, status=400)
            
            # Проверяем формат ссылки
            import re
            telegram_regex = re.compile(r'^https?://t\.me/[a-zA-Z0-9_]{5,32}$')
            if not telegram_regex.match(telegram_link):
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный формат ссылки Telegram'
                }, status=400)
            
            # Проверяем, не подключен ли уже Telegram
            if user.telegram_link:
                return JsonResponse({
                    'success': False,
                    'error': 'Telegram уже подключен. Для изменения обратитесь в поддержку.'
                }, status=400)
            
            # Сохраняем ссылку
            user.telegram_link = telegram_link
            user.save()
            
            print(f"✅ Telegram сохранен для пользователя {user.username}: {telegram_link}")
            
            return JsonResponse({
                'success': True,
                'message': 'Telegram успешно подключен',
                'telegram_link': telegram_link
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при сохранении Telegram:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RemoveTelegramAPIView(View):
    """
    API View для отключения Telegram
    """
    def post(self, request):
        try:
            print("=== ОТКЛЮЧЕНИЕ TELEGRAM ===")
            
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
            
            # Отключаем Telegram
            user.telegram_link = None
            user.save()
            
            print(f"✅ Telegram отключен для пользователя {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Telegram успешно отключен'
            })
            
        except Token.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный токен'
            }, status=401)
        except Exception as e:
            print("Ошибка при отключении Telegram:", str(e))
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)