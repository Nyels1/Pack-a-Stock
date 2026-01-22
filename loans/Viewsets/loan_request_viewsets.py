from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from loans.models import LoanRequest
from loans.Serializers.loan_request_serializer import (
    LoanRequestSerializer,
    LoanRequestCreateSerializer
)


class LoanRequestViewSet(viewsets.ModelViewSet):
    queryset = LoanRequest.objects.all()
    serializer_class = LoanRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'requester', 'desired_pickup_date']
    search_fields = ['purpose', 'requester__full_name']
    ordering_fields = ['requested_date', 'desired_pickup_date', 'status']
    
    def get_queryset(self):
        user = self.request.user
        queryset = LoanRequest.objects.filter(account=user.account)
        
        # Si es empleado, solo ver sus propias solicitudes
        if user.user_type == 'employee':
            queryset = queryset.filter(requester=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LoanRequestCreateSerializer
        return LoanRequestSerializer
    
    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account, requester=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar solicitud de préstamo"""
        loan_request = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            loan_request.approve(request.user, notes)
            return Response({
                'status': 'success',
                'message': 'Solicitud aprobada'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar solicitud de préstamo"""
        loan_request = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            loan_request.reject(request.user, notes)
            return Response({
                'status': 'success',
                'message': 'Solicitud rechazada'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener solicitudes pendientes"""
        pending_requests = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Obtener solicitudes del usuario actual"""
        my_requests = self.get_queryset().filter(requester=request.user)
        serializer = self.get_serializer(my_requests, many=True)
        return Response(serializer.data)
