from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Account
from accounts.Serializers.account_serializer import AccountSerializer
from pack_a_stock_api.permissions import IsAdminOrSuperUser
import logging

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Account.objects.all()
        return Account.objects.filter(id=user.account.id)
    
    def get_permissions(self):
        """Permisos específicos según la acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
            return [IsAuthenticated(), IsAdminOrSuperUser()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        account = self.get_object()
        account.is_active = True
        account.save()
        logger.info(f'Cuenta activada: {account.company_name} por {request.user.email}')
        return Response({'status': 'Cuenta activada'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        account = self.get_object()
        account.is_active = False
        account.save()
        logger.warning(f'Cuenta desactivada: {account.company_name} por {request.user.email}')
        return Response({'status': 'Cuenta desactivada'})
