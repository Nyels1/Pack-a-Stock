from django.urls import path
from accounts.Viewsets.admin_viewsets import (
    admin_stats,
    admin_accounts,
    admin_update_account,
    admin_delete_account,
    admin_payments,
    admin_users,
    admin_toggle_user,
)

urlpatterns = [
    path('stats/', admin_stats, name='admin_stats'),
    path('accounts/', admin_accounts, name='admin_accounts'),
    path('accounts/<int:pk>/', admin_update_account, name='admin_update_account'),
    path('accounts/<int:pk>/delete/', admin_delete_account, name='admin_delete_account'),
    path('payments/', admin_payments, name='admin_payments'),
    path('users/', admin_users, name='admin_users'),
    path('users/<int:pk>/toggle/', admin_toggle_user, name='admin_toggle_user'),
]
