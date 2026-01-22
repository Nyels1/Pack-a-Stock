from rest_framework import routers
from accounts.Viewsets.account_viewsets import AccountViewSet
from accounts.Viewsets.user_viewsets import UserViewSet


router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'users', UserViewSet)
