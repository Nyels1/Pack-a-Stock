from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class Account(models.Model):
    PLAN_CHOICES = [
        ('freemium', 'Freemium'),
        ('premium', 'Premium'),
    ]
    
    company_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True)
    exterior_number = models.CharField(max_length=50, blank=True)
    interior_number = models.CharField(max_length=50, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, default='México')
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    
    subscription_plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='freemium')
    max_locations = models.IntegerField(default=1)
    max_users = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['subscription_plan']),
        ]
    
    def __str__(self):
        return self.company_name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'inventarista')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('inventarista', 'Inventarista'),
        ('employee', 'Empleado'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='users')
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='employee')
    
    face_encoding = models.TextField(blank=True, null=True)
    
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_blocked']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def has_perm(self, perm, obj=None):
        """Superusers tienen todos los permisos"""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """Superusers tienen permisos en todos los módulos"""
        return self.is_superuser

