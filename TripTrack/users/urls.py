from django.urls import path
from .views import (
    CustomUserRegistrationAPIView,
    CustomUserLoginAPIView,
    CustomUserLogoutAPIView,  # Добавляем новый view
    VerifyAuthAPIView,
    TestAPIView,
    UserBalanceAPIView,           # Новые views
    UserTransactionsAPIView,      # Новые views  
    UserBalanceSummaryAPIView,    # Новые views
)

urlpatterns = [
    path('register/', CustomUserRegistrationAPIView.as_view(), name='register'),
    path('login/', CustomUserLoginAPIView.as_view(), name='login'),
    path('logout/', CustomUserLogoutAPIView.as_view(), name='logout'),  # Новый маршрут
    path('verify/', VerifyAuthAPIView.as_view(), name='verify'),
    path('test/', TestAPIView.as_view(), name='test'),
    path('balance/', UserBalanceAPIView.as_view(), name='balance'),
    path('transactions/', UserTransactionsAPIView.as_view(), name='transactions'),
    path('balance-summary/', UserBalanceSummaryAPIView.as_view(), name='balance_summary'),
]