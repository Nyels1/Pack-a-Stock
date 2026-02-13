from django.contrib import admin
from .models import Account, User, SubscriptionPlan, Payment


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'subscription_plan', 'max_locations', 'max_users', 'is_active']
    list_filter = ['subscription_plan', 'is_active']
    search_fields = ['company_name', 'email']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'user_type', 'account', 'is_blocked', 'is_active']
    list_filter = ['user_type', 'is_blocked', 'is_active']
    search_fields = ['email', 'full_name']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('full_name', 'user_type', 'account')}),
        ('Bloqueo', {'fields': ('is_blocked', 'blocked_reason', 'blocked_until')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    ordering = ('-created_at',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'price', 'duration_days', 'is_active']
    list_filter = ['is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['account', 'plan', 'amount', 'card_last_four', 'status', 'paid_at']
    list_filter = ['status', 'plan']
    search_fields = ['account__company_name', 'card_holder_name']

