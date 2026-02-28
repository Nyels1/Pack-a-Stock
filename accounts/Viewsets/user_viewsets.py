from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from accounts.models import User
from accounts.Serializers.user_serializer import (
    UserSerializer, 
    UserCreateSerializer, 
    RegisterSerializer, 
    LoginSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all().order_by('id')
        return User.objects.filter(account=user.account).order_by('id')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Registro de nueva cuenta y usuario administrador"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login de usuario"""
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Actualizar último login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Bloquear usuario"""
        user = self.get_object()
        user.is_blocked = True
        user.blocked_reason = request.data.get('reason', '')
        user.blocked_until = request.data.get('blocked_until')
        user.save()
        return Response({'status': 'Usuario bloqueado'})
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Desbloquear usuario"""
        user = self.get_object()
        user.is_blocked = False
        user.blocked_reason = None
        user.blocked_until = None
        user.save()
        return Response({'status': 'Usuario desbloqueado'})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def check_delete(self, request, pk=None):
        from loans.models import Loan, LoanRequest
        user = self.get_object()
        active_loans = Loan.objects.filter(borrower=user, status__in=['active', 'approved'])
        pending_requests = LoanRequest.objects.filter(requested_by=user, status='pending')
        return Response({
            'can_delete': True,
            'active_loans_count': active_loans.count(),
            'pending_requests_count': pending_requests.count(),
            'loan_material_names': list(active_loans.values_list('material__name', flat=True)[:10]),
        })
