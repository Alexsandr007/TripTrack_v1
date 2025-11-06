from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для пользователей с поиском без учета регистра
    """
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным username, email и password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)
    
    def exists_by_username(self, username):
        """Проверка существования пользователя по username (без учета регистра)"""
        return self.filter(username__iexact=username).exists()
    
    def exists_by_email(self, email):
        """Проверка существования пользователя по email (без учета регистра)"""
        return self.filter(email__iexact=email).exists()



class CustomUser(AbstractUser):
    mentor_login = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    
    # Поля баланса (добавляем прямо в модель пользователя)
    balance_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Баланс'
    )
    balance_currency = models.CharField(
        max_length=3, 
        default='RUB',
        choices=[('RUB', 'Рубли'), ('USD', 'Доллары'), ('EUR', 'Евро')],
        verbose_name='Валюта баланса'
    )
    balance_updated_at = models.DateTimeField(auto_now=True, verbose_name='Баланс обновлен')
    
    # Добавляем кастомный менеджер
    objects = CustomUserManager()
    
    # Обязательно добавляем related_name чтобы избежать конфликтов
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )
    
    def save(self, *args, **kwargs):
        # Приводим username и email к нижнему регистру перед сохранением
        if self.username:
            self.username = self.username.lower()
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    @property
    def balance(self):
        """Property для удобного доступа к данным баланса"""
        return {
            'amount': self.balance_amount,
            'currency': self.balance_currency,
            'currency_display': self.get_balance_currency_display(),
            'updated_at': self.balance_updated_at
        }
    
    def get_balance_display(self):
        """Форматированное отображение баланса"""
        return f"{self.balance_amount} {self.get_balance_currency_display()}"
    
    def __str__(self):
        return self.username


class Transaction(models.Model):
    """
    Модель транзакции пользователя
    """
    TRANSACTION_TYPES = [
        ('income', 'Пополнение'),
        ('outcome', 'Вывод'),
        ('bonus', 'Бонус'),
        ('Pay', 'Выплата'),
        ('transfer', 'Перевод'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='RUB')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10, 
        default='completed',
        choices=[('pending', 'В обработке'), ('completed', 'Завершено'), ('failed', 'Ошибка')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_transactions'
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.amount} {self.currency} - {self.get_transaction_type_display()}"
    

class UserMentorRelationship(models.Model):
    """
    Модель для связи пользователя и ментора
    """
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='mentor_relationship_as_user'
    )
    mentor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='mentor_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_mentor_relationships'
        verbose_name = 'Связь пользователь-ментор'
        verbose_name_plural = 'Связи пользователь-ментор'

    def __str__(self):
        return f"{self.user.username} -> {self.mentor.username}"