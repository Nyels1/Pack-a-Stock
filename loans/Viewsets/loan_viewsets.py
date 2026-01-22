from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from loans.models import Loan
from loans.Serializers.loan_serializer import (
    LoanSerializer,
    LoanCreateSerializer,
    LoanReturnSerializer
)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'borrower', 'material', 'is_consumable_loan']
    search_fields = ['borrower__full_name', 'material__name']
    ordering_fields = ['issued_at', 'expected_return_date', 'status']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Loan.objects.filter(account=user.account)
        
        # Si es empleado, solo ver sus propios préstamos
        if user.user_type == 'employee':
            queryset = queryset.filter(borrower=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LoanCreateSerializer
        return LoanSerializer
    
    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account, issued_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def return_loan(self, request, pk=None):
        """Registrar devolución de préstamo"""
        loan = self.get_object()
        serializer = LoanReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            loan.return_loan(
                inventarista=request.user,
                condition=serializer.validated_data['condition_on_return'],
                damage_notes=serializer.validated_data.get('damage_notes', ''),
                signature=serializer.validated_data.get('return_signature', '')
            )
            return Response({
                'status': 'success',
                'message': 'Préstamo devuelto exitosamente'
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener préstamos activos"""
        active_loans = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Obtener préstamos vencidos"""
        overdue_loans = self.get_queryset().filter(status='overdue')
        serializer = self.get_serializer(overdue_loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """Obtener préstamos del usuario actual"""
        my_loans = self.get_queryset().filter(borrower=request.user)
        serializer = self.get_serializer(my_loans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_facial_auth(self, request, pk=None):
        """Verificar autenticación facial"""
        loan = self.get_object()
        loan.facial_auth_verified = True
        loan.facial_auth_at = timezone.now()
        loan.save()
        return Response({
            'status': 'success',
            'message': 'Autenticación facial verificada'
        })
