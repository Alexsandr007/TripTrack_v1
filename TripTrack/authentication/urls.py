from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import YourViewSet  # Добавьте ваши views

router = DefaultRouter()
# router.register(r'auth', YourViewSet)  # Пример

urlpatterns = [
    path('', include(router.urls)),
]