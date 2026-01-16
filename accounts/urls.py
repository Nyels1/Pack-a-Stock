from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, UserViewSet, register_view, login_view, logout_view

router = DefaultRouter()
router.register('accounts', AccountViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
