# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CustomUserRegistrationAPIView.as_view(), name='register'),
    path('login/', views.CustomUserLoginAPIView.as_view(), name='login'),
    path('logout/', views.CustomUserLogoutAPIView.as_view(), name='logout'),
    path('verify/', views.VerifyAuthAPIView.as_view(), name='verify-auth'),
    path('balance/', views.UserBalanceAPIView.as_view(), name='user-balance'),
    path('transactions/', views.UserTransactionsAPIView.as_view(), name='user-transactions'),
    path('balance-summary/', views.UserBalanceSummaryAPIView.as_view(), name='balance-summary'),
    
    # Новые URLs для обновлений через WebSocket
    path('update-balance/', views.UpdateBalanceAPIView.as_view(), name='update-balance'),
    path('create-transaction/', views.CreateTransactionAPIView.as_view(), name='create-transaction'),
    
    # Реферальные URLs
    path('referral-stats/', views.ReferralStatsAPIView.as_view(), name='referral-stats'),
    path('referral-link/', views.ReferralLinkAPIView.as_view(), name='referral-link'),
    path('get-mentor-by-ref/', views.GetMentorByReferralCodeView.as_view(), name='get-mentor-by-ref'),
]