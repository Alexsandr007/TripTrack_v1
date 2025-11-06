from django.urls import path
from .views import (
    CustomUserRegistrationAPIView,
    VerifyAuthAPIView,
    TestAPIView
)

urlpatterns = [
    path('register/', CustomUserRegistrationAPIView.as_view(), name='register'),
    path('verify/', VerifyAuthAPIView.as_view(), name='verify'),
    path('test/', TestAPIView.as_view(), name='test'),
]