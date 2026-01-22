from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from accounts.Serializers.account_serializer import AccountSerializer


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'account', 'email', 'full_name', 'user_type', 'is_blocked',
            'blocked_reason', 'blocked_until', 'is_active', 'created_at',
            'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'user_type']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)
    company_name = serializers.CharField(max_length=255)
    street = serializers.CharField(max_length=255, required=False, allow_blank=True)
    exterior_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    interior_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=255, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    city = serializers.CharField(max_length=255, required=False, allow_blank=True)
    state = serializers.CharField(max_length=255, required=False, allow_blank=True)
    country = serializers.CharField(max_length=255, default='México')
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    subscription_plan = serializers.ChoiceField(choices=['freemium', 'premium'], default='freemium')
    
    def create(self, validated_data):
        # Extraer datos de la cuenta
        account_data = {
            'company_name': validated_data.pop('company_name'),
            'street': validated_data.pop('street', ''),
            'exterior_number': validated_data.pop('exterior_number', ''),
            'interior_number': validated_data.pop('interior_number', ''),
            'neighborhood': validated_data.pop('neighborhood', ''),
            'postal_code': validated_data.pop('postal_code', ''),
            'city': validated_data.pop('city', ''),
            'state': validated_data.pop('state', ''),
            'country': validated_data.pop('country', 'México'),
            'phone': validated_data.pop('phone', ''),
            'email': validated_data['email'],
            'subscription_plan': validated_data.pop('subscription_plan', 'freemium'),
        }
        
        # Crear cuenta
        account = Account.objects.create(**account_data)
        
        # Crear usuario administrador
        user = User.objects.create_user(
            account=account,
            user_type='inventarista',
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Credenciales inválidas')
            
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo')
            
            if user.is_blocked:
                raise serializers.ValidationError('Usuario bloqueado')
        else:
            raise serializers.ValidationError('Email y contraseña son requeridos')
        
        data['user'] = user
        return data
