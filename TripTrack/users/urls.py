# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('verify/', views.verify_auth, name='verify_auth'),
    path('check-token/', views.check_token, name='check_token'),  # Добавьте этот маршрут
    # ... другие маршруты
]