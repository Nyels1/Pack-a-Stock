from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Account, User
from .serializers import (
    AccountSerializer, UserSerializer, UserCreateSerializer,
    RegisterSerializer, LoginSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'inventarista':
            return Account.objects.filter(id=user.account.id)
        return Account.objects.none()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(account=user.account)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type != 'inventarista':
            raise PermissionError("Solo inventaristas pueden crear usuarios")
        
        current_users_count = User.objects.filter(account=user.account).count()
        if user.account.max_users != -1 and current_users_count >= user.account.max_users:
            raise PermissionError(f"Has alcanzado el límite de {user.account.max_users} usuarios para tu plan")
        
        serializer.save(account=user.account, user_type='employee')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def block(self, request, pk=None):
        user = self.get_object()
        if request.user.user_type != 'inventarista':
            return Response(
                {'error': 'Solo inventaristas pueden bloquear usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_blocked = request.data.get('is_blocked', True)
        blocked_reason = request.data.get('blocked_reason', '')
        blocked_until = request.data.get('blocked_until', None)
        
        user.is_blocked = is_blocked
        user.blocked_reason = blocked_reason
        user.blocked_until = blocked_until
        user.save()
        
        return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        account = result['account']
        user = result['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'account': AccountSerializer(account).data,
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Sesión cerrada exitosamente'})
    except Exception:
        return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

