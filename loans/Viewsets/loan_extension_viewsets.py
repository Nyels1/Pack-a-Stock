from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from loans.models import LoanExtension
from loans.Serializers.loan_extension_serializer import (
    LoanExtensionSerializer,
    LoanExtensionCreateSerializer
)


class LoanExtensionViewSet(viewsets.ModelViewSet):
    queryset = LoanExtension.objects.all()
    serializer_class = LoanExtensionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'loan']
    ordering_fields = ['requested_at', 'status']
    
    def get_queryset(self):
        user = self.request.user
        return LoanExtension.objects.filter(loan__account=user.account)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LoanExtensionCreateSerializer
        return LoanExtensionSerializer
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar extensión de préstamo"""
        extension = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            extension.approve(request.user, notes)
            return Response({
                'status': 'success',
                'message': 'Extensión aprobada'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar extensión de préstamo"""
        extension = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            extension.reject(request.user, notes)
            return Response({
                'status': 'success',
                'message': 'Extensión rechazada'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener extensiones pendientes"""
        pending = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
