# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirmPassword = serializers.CharField(write_only=True)
    fullName = serializers.CharField(source='first_name')
    login = serializers.CharField(source='username')
    Mentorlogin = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('fullName', 'login', 'email', 'password', 'confirmPassword', 'Mentorlogin')

    def validate(self, data):
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError("Пароли не совпадают")
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")
            
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
            
        return data

    def create(self, validated_data):
        # Удаляем confirmPassword и Mentorlogin из данных для создания пользователя
        validated_data.pop('confirmPassword')
        mentor_login = validated_data.pop('Mentorlogin')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name']
        )
        
        # Здесь можно сохранить mentor_login в профиль пользователя
        # если у вас есть расширенная модель
        return user