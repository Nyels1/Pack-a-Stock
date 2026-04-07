from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts import views
from accounts.Viewsets.subscription_viewsets import (
    list_plans,
    subscribe,
    payment_history,
    subscription_status,
)

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('register-employee/', views.register_employee_view, name='register_employee'),
    path('login/', views.login_view, name='login'),
    path('firebase/', views.firebase_auth_view, name='firebase_auth'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile
    path('me/', views.me_view, name='me'),
    path('me/update/', views.update_profile_view, name='update_profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    # Users management (inventaristas only)
    path('users/', views.UserListCreateView.as_view(), name='users_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/block/', views.block_user_view, name='block_user'),

    # Subscriptions
    path('plans/', list_plans, name='list_plans'),
    path('subscribe/', subscribe, name='subscribe'),
    path('payments/', payment_history, name='payment_history'),
    path('subscription/', subscription_status, name='subscription_status'),
]
