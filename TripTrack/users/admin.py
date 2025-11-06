from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Transaction


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Отображение в списке
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'full_name',
        'mentor_login',
        'balance_amount',
        'balance_currency',
        'balance_updated_at',
        'is_staff', 
        'is_active', 
        'date_joined',
        'last_login'
    )
    
    # Поля для фильтрации
    list_filter = (
        'is_staff', 
        'is_active', 
        'is_superuser',
        'balance_currency',
        'date_joined',
        'last_login'
    )
    
    # Поля для поиска
    search_fields = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'full_name',
        'mentor_login'
    )
    
    # Порядок отображения
    ordering = ('-date_joined',)
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'username', 
                'email', 
                'password',
                'first_name',
                'last_name',
                'full_name'
            )
        }),
        ('Информация о менторе', {
            'fields': ('mentor_login',)
        }),
        ('Баланс', {
            'fields': (
                'balance_amount',
                'balance_currency',
                'balance_updated_at'
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Важные даты', {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('balance_updated_at', 'last_login', 'date_joined')
    
    # Поля в форме добавления пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2',
                'first_name',
                'last_name',
                'full_name',
                'mentor_login',
                'balance_amount',
                'balance_currency',
                'is_active',
                'is_staff'
            )}
        ),
    )
    
    # Действия для админ-панели
    actions = ['reset_balances', 'activate_users', 'deactivate_users']
    
    def reset_balances(self, request, queryset):
        """Сбросить баланс выбранных пользователей"""
        updated = queryset.update(balance_amount=0)
        self.message_user(request, f'Баланс сброшен для {updated} пользователей')
    reset_balances.short_description = "Сбросить баланс выбранных пользователей"
    
    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} пользователей')
    activate_users.short_description = "Активировать выбранных пользователей"
    
    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} пользователей')
    deactivate_users.short_description = "Деактивировать выбранных пользователей"

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = (
        'id',
        'user',
        'amount',
        'currency',
        'transaction_type',
        'type_display',
        'description',
        'status',
        'created_at'
    )
    
    # Поля для фильтрации
    list_filter = (
        'transaction_type',
        'status',
        'currency',
        'created_at'
    )
    
    # Поля для поиска
    search_fields = (
        'user__username',
        'user__email',
        'description',
        'amount'
    )
    
    # Порядок отображения
    ordering = ('-created_at',)
    
    # Поля только для чтения
    readonly_fields = ('created_at',)
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'amount',
                'currency',
                'transaction_type',
                'description'
            )
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Автозаполнение поля
    def type_display(self, obj):
        return obj.get_transaction_type_display()
    type_display.short_description = 'Тип операции'
    
    # Действия для админ-панели
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        """Пометить как завершенные"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'Отмечено как завершенные: {updated} транзакций')
    mark_as_completed.short_description = "Пометить как завершенные"
    
    def mark_as_failed(self, request, queryset):
        """Пометить как ошибки"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'Отмечено как ошибки: {updated} транзакций')
    mark_as_failed.short_description = "Пометить как ошибки"