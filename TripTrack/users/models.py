from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(models.Manager):
    """
    Кастомный менеджер для пользователей с поиском без учета регистра
    """
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
    
    def __str__(self):
        return self.username
    

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