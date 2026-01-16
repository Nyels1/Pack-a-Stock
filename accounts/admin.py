from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account, User


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'subscription_plan', 'max_locations', 'max_users', 'is_active']
    list_filter = ['subscription_plan', 'is_active']
    search_fields = ['company_name', 'email']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'user_type', 'account', 'is_blocked', 'is_active']
    list_filter = ['user_type', 'is_blocked', 'is_active']
    search_fields = ['email', 'full_name']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('full_name', 'user_type', 'account')}),
        ('Bloqueo', {'fields': ('is_blocked', 'blocked_reason', 'blocked_until')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'account', 'user_type', 'password1', 'password2'),
        }),
    )
    
    ordering = ('-created_at',)

