from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from users.models import CustomUser, Transaction


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных кастомного пользователя
    """
    fullName = serializers.CharField(source='full_name', read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'fullName', 'mentor_login', 'balance')

    def get_balance(self, obj):
        """Получаем данные баланса"""
        return {
            'amount': str(obj.balance_amount),
            'currency': obj.balance_currency,
            'currency_display': obj.get_balance_currency_display(),
            'updated_at': obj.balance_updated_at.strftime('%d.%m.%Y %H:%M')
        }


class UserBalanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для баланса пользователя
    """
    amount = serializers.DecimalField(source='balance_amount', max_digits=10, decimal_places=2, read_only=True)
    currency = serializers.CharField(source='balance_currency', read_only=True)
    currency_display = serializers.CharField(source='get_balance_currency_display', read_only=True)
    updated_at = serializers.DateTimeField(source='balance_updated_at', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('amount', 'currency', 'currency_display', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для транзакций пользователя
    """
    amount_display = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    date = serializers.DateTimeField(source='created_at', format='%d.%m.%Y')
    
    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'amount_display', 'currency', 'transaction_type', 
                 'type_display', 'description', 'status', 'date')
    
    def get_amount_display(self, obj):
        """
        Форматируем сумму с знаком +/-
        """
        if obj.transaction_type in ['income', 'bonus', 'task']:
            return f"+{obj.amount}"
        else:
            return f"-{obj.amount}"


class CustomUserRegistrationSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации кастомного пользователя
    """
    fullName = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={'required': 'Полное имя обязательно'}
    )
    login = serializers.CharField(
        write_only=True,
        required=True,
        min_length=3,
        error_messages={
            'required': 'Логин обязателен',
            'min_length': 'Логин должен содержать минимум 3 символа'
        }
    )
    email = serializers.EmailField(
        write_only=True,
        required=True,
        error_messages={'required': 'Email обязателен'}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        error_messages={
            'required': 'Пароль обязателен',
            'min_length': 'Пароль должен содержать минимум 6 символов'
        }
    )
    confirmPassword = serializers.CharField(write_only=True, required=True)
    Mentorlogin = serializers.CharField(
        write_only=True, 
        required=True,
        error_messages={'required': 'Логин ментора обязателен'}
    )
    referral_code = serializers.CharField(
        write_only=True,
        required=False, 
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = ('fullName', 'login', 'email', 'password', 'confirmPassword', 'Mentorlogin', 'referral_code')

    def validate(self, attrs):
        # Проверка совпадения паролей
        if attrs['password'] != attrs['confirmPassword']:
            raise serializers.ValidationError({
                'confirmPassword': ['Пароли не совпадают']
            })

        # Валидация сложности пароля
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        # Проверка уникальности username (без учета регистра)
        username = attrs['login']
        username_lower = username.lower()
        
        # Ищем пользователей с таким же логином (без учета регистра)
        existing_users = CustomUser.objects.filter(username__iexact=username_lower)
        if existing_users.exists():
            raise serializers.ValidationError({
                'login': [f'Пользователь с логином "{username}" уже существует (регистр не учитывается)']
            })

        # Проверка уникальности email (без учета регистра)
        email = attrs['email']
        email_lower = email.lower()
        
        # Ищем пользователей с таким же email (без учета регистра)
        existing_emails = CustomUser.objects.filter(email__iexact=email_lower)
        if existing_emails.exists():
            raise serializers.ValidationError({
                'email': [f'Пользователь с email "{email}" уже существует (регистр не учитывается)']
            })

        # ПРОВЕРКА СУЩЕСТВОВАНИЯ МЕНТОРА (без учета регистра)
        mentor_login = attrs['Mentorlogin']
        mentor_login_lower = mentor_login.lower()
        
        if not CustomUser.objects.filter(username__iexact=mentor_login_lower).exists():
            raise serializers.ValidationError({
                'Mentorlogin': [f'Ментор с логином "{mentor_login}" не существует']
            })

        # ВАЛИДАЦИЯ РЕФЕРАЛЬНОГО КОДА - ОСНОВНАЯ ЛОГИКА
        referral_code = attrs.get('referral_code', '').strip()
        
        if referral_code:
            # Проверяем существование реферального кода
            try:
                referring_user = CustomUser.objects.get(referral_code=referral_code)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({
                    'referral_code': [f'Реферальный код "{referral_code}" не найден']
                })
            
            # Проверяем, что реферер не регистрирует сам себя
            username_lower = attrs['login'].lower()
            if referring_user.username.lower() == username_lower:
                raise serializers.ValidationError({
                    'referral_code': ['Нельзя использовать собственный реферальный код']
                })
            
            # ✅ АВТОМАТИЧЕСКИ устанавливаем реферера как ментора!
            # Ментор и реферер - это один человек
            attrs['Mentorlogin'] = referring_user.username
            attrs['referring_user'] = referring_user
            
            print(f"✅ Автоматически установлен ментор: {referring_user.username}")

        else:
            # Если нет реферального кода, проверяем существование ментора
            mentor_login = attrs['Mentorlogin']
            mentor_login_lower = mentor_login.lower()
            
            if not CustomUser.objects.filter(username__iexact=mentor_login_lower).exists():
                raise serializers.ValidationError({
                    'Mentorlogin': [f'Ментор с логином "{mentor_login}" не существует']
                })

        return attrs

    def create(self, validated_data):
        """
        Создание кастомного пользователя с поддержкой реферальной системы
        """
        # Получаем ментора из базы данных (без учета регистра)
        mentor_login = validated_data['Mentorlogin']
        mentor = CustomUser.objects.get(username__iexact=mentor_login.lower())
        
        # Получаем реферера, если есть (это тот же человек что и ментор!)
        referring_user = validated_data.pop('referring_user', None)
        referral_code = validated_data.pop('referral_code', None)
        
        # Приводим логин и email к нижнему регистру для хранения
        username_lower = validated_data['login'].lower()
        email_lower = validated_data['email'].lower()
        
        # Создаем пользователя
        user = CustomUser.objects.create_user(
            username=username_lower,
            email=email_lower,
            password=validated_data['password'],
            first_name=validated_data['fullName'],
            full_name=validated_data['fullName'],
            mentor_login=mentor_login,
        )
        
        # Устанавливаем реферера (это тот же человек что и ментор!)
        if referring_user:
            user.referred_by = referring_user
            user.save()
            
            # Обновляем счетчик рефералов у реферера/ментора
            referring_user.refresh_from_db()
            referring_user.referral_count = referring_user.referrals.count()
            referring_user.save()
            
            print(f"✅ Пользователь {user.username} зарегистрирован:")
            print(f"   - Ментор/Реферер: {referring_user.username}")
            print(f"   - Ученик/Реферал: {user.username}")
            print(f"   - Новое количество рефералов: {referring_user.referral_count}")
            
            # Отправляем WebSocket уведомление рефереру/ментору
            try:
                from .websocket_utils import send_referral_update
                send_referral_update(referring_user.id, {
                    'referral_count': referring_user.referral_count,
                    'active_referrals_count': referring_user.active_referrals_count,
                    'new_referral': {
                        'username': user.username,
                        'full_name': user.full_name,
                        'registration_date': user.date_joined.isoformat()
                    }
                })
                print(f"📨 WebSocket уведомление отправлено ментору {referring_user.username}")
            except Exception as e:
                print(f"❌ Ошибка отправки WebSocket уведомления: {e}")
        
        return user