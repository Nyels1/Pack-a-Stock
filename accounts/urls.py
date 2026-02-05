from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('me/', views.me_view, name='me'),
    path('me/update/', views.update_profile_view, name='update_profile'),
    
    # Users management (inventaristas only)
    path('users/', views.UserListCreateView.as_view(), name='users_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/block/', views.block_user_view, name='block_user'),
]
