from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Account, User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'company_name', 'street', 'exterior_number', 'interior_number',
            'neighborhood', 'postal_code', 'city', 'state', 'country', 'phone',
            'email', 'subscription_plan', 'max_locations', 'max_users', 'is_active',
            'subscription_start_date', 'subscription_end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'max_locations', 'max_users']


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
    company_email = serializers.EmailField()
    subscription_plan = serializers.ChoiceField(choices=['freemium', 'premium'], default='freemium')
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value
    
    def validate_company_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email de empresa ya está registrado")
        return value
    
    def create(self, validated_data):
        account_data = {
            'company_name': validated_data['company_name'],
            'email': validated_data['company_email'],
            'street': validated_data.get('street', ''),
            'exterior_number': validated_data.get('exterior_number', ''),
            'interior_number': validated_data.get('interior_number', ''),
            'neighborhood': validated_data.get('neighborhood', ''),
            'postal_code': validated_data.get('postal_code', ''),
            'city': validated_data.get('city', ''),
            'state': validated_data.get('state', ''),
            'country': validated_data.get('country', 'México'),
            'phone': validated_data.get('phone', ''),
            'subscription_plan': validated_data.get('subscription_plan', 'freemium'),
        }
        
        if account_data['subscription_plan'] == 'freemium':
            account_data['max_locations'] = 1
            account_data['max_users'] = 5
        else:
            account_data['max_locations'] = -1
            account_data['max_users'] = -1
        
        account = Account.objects.create(**account_data)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            user_type='inventarista',
            account=account
        )
        
        return {'account': account, 'user': user}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas")
            if not user.is_active:
                raise serializers.ValidationError("Usuario inactivo")
            if user.is_blocked:
                raise serializers.ValidationError("Usuario bloqueado")
        else:
            raise serializers.ValidationError("Debe incluir email y contraseña")
        
        data['user'] = user
        return data
