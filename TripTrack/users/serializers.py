from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных кастомного пользователя
    """
    fullName = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'fullName', 'mentor_login')
        read_only_fields = ('id',)


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
    Mentorlogin = serializers.CharField(write_only=True, required=True)

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

        # Проверка уникальности username
        username = attrs['login']
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'login': ['Пользователь с таким логином уже существует']
            })

        # Проверка уникальности email
        email = attrs['email']
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': ['Пользователь с таким email уже существует']
            })

        return attrs

    def create(self, validated_data):
        """
        Создание кастомного пользователя
        """
        user = CustomUser.objects.create_user(
            username=validated_data['login'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullName'],  # сохраняем в first_name
            full_name=validated_data['fullName'],   # и в full_name
            mentor_login=validated_data['Mentorlogin']
        )
        return user