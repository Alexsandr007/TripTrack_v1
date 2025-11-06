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


# Остальные сериализаторы остаются без изменений
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

        return attrs

    def create(self, validated_data):
        """
        Создание кастомного пользователя
        """
        # Получаем ментора из базы данных (без учета регистра)
        mentor_login = validated_data['Mentorlogin']
        mentor = CustomUser.objects.get(username__iexact=mentor_login.lower())
        
        # Приводим логин и email к нижнему регистру для хранения
        username_lower = validated_data['login'].lower()
        email_lower = validated_data['email'].lower()
        
        user = CustomUser.objects.create_user(
            username=username_lower,
            email=email_lower,
            password=validated_data['password'],
            first_name=validated_data['fullName'],
            full_name=validated_data['fullName'],
            mentor_login=validated_data['Mentorlogin'],
            # Баланс устанавливается автоматически по умолчанию (0.00 RUB)
        )
        
        print(f"Пользователь {user.username} зарегистрирован с ментором {mentor.username}")
        
        return user