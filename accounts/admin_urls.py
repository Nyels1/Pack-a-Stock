from django.urls import path
from accounts.Viewsets.admin_viewsets import (
    admin_stats,
    admin_accounts,
    admin_update_account,
    admin_payments,
    admin_users,
)

urlpatterns = [
    path('stats/', admin_stats, name='admin_stats'),
    path('accounts/', admin_accounts, name='admin_accounts'),
    path('accounts/<int:pk>/', admin_update_account, name='admin_update_account'),
    path('payments/', admin_payments, name='admin_payments'),
    path('users/', admin_users, name='admin_users'),
]
