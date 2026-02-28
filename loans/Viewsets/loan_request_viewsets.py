from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
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
        user = self.request.user
        if user.is_blocked:
            raise PermissionDenied('No puedes crear solicitudes mientras tengas una penalización activa.')
        serializer.save(account=user.account, requester=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Return full data (id, qr_token, status, etc.) instead of the create serializer
        full_serializer = LoanRequestSerializer(
            serializer.instance, context={'request': request}
        )
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar solicitud de préstamo - devuelve qr_token para Flutter"""
        loan_request = self.get_object()
        notes = request.data.get('notes', '')

        try:
            loan_request.approve(request.user, notes)
            serializer = self.get_serializer(loan_request)
            return Response({
                'status': 'success',
                'message': 'Solicitud aprobada',
                'qr_token': str(loan_request.qr_token),
                'data': serializer.data
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

    @action(detail=False, methods=['get'], url_path='by-qr/(?P<qr_token>[^/.]+)')
    def by_qr(self, request, qr_token=None):
        """Buscar solicitud por QR token"""
        try:
            loan_request = self.get_queryset().get(qr_token=qr_token)
            serializer = self.get_serializer(loan_request)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except LoanRequest.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
