from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Account
from accounts.Serializers.account_serializer import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Account.objects.all()
        return Account.objects.filter(id=user.account.id)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        account = self.get_object()
        account.is_active = True
        account.save()
        return Response({'status': 'Cuenta activada'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        account = self.get_object()
        account.is_active = False
        account.save()
        return Response({'status': 'Cuenta desactivada'})
