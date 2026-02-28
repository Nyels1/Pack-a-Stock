from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from accounts.models import User, Account
from accounts.Serializers.user_serializer import (
    UserSerializer, 
    RegisterSerializer, 
    LoginSerializer,
    UserCreateSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Registro de nueva cuenta con inventarista principal
    POST /api/auth/register
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Actualizar last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'message': 'Cuenta creada exitosamente',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login con JWT
    POST /api/auth/login
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Actualizar last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout (invalidar refresh token)
    POST /api/auth/logout
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error al cerrar sesión'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Obtener perfil del usuario autenticado
    GET /api/auth/me
    """
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Actualizar perfil del usuario autenticado
    PUT /api/auth/me
    """
    user = request.user
    allowed_fields = ['full_name']
    
    for field in allowed_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    
    user.save()
    
    serializer = UserSerializer(user)
    return Response({
        'success': True,
        'message': 'Perfil actualizado exitosamente',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


class UserListCreateView(generics.ListCreateAPIView):
    """
    Listar y crear usuarios (empleados) - Solo inventaristas
    GET/POST /api/users/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        # Filtrar por cuenta del usuario autenticado
        return User.objects.filter(account=self.request.user.account)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        # Verificar que es inventarista
        if self.request.user.user_type != 'inventarista':
            raise PermissionDenied('Solo los inventaristas pueden crear usuarios')
        
        # Verificar límite de usuarios según plan
        account = self.request.user.account
        current_users = User.objects.filter(account=account).count()
        
        if account.max_users != -1 and current_users >= account.max_users:
            raise ValidationError({
                'error': 'USERS_LIMIT_REACHED',
                'message': 'Has alcanzado el límite de usuarios para tu plan',
                'details': {
                    'current_plan': account.subscription_plan,
                    'max_users': account.max_users,
                    'current_users': current_users
                }
            })
        
        # Asignar cuenta del usuario autenticado
        serializer.save(account=self.request.user.account)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Ver, actualizar o eliminar un usuario - Solo inventaristas
    GET/PUT/DELETE /api/users/:id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        # Solo usuarios de la misma cuenta
        return User.objects.filter(account=self.request.user.account)
    
    def perform_update(self, serializer):
        if self.request.user.user_type != 'inventarista':
            raise PermissionDenied('Solo los inventaristas pueden modificar usuarios')
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user.user_type != 'inventarista':
            raise PermissionDenied('Solo los inventaristas pueden eliminar usuarios')
        instance.delete()


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def block_user_view(request, pk):
    """
    Bloquear/desbloquear usuario - Solo inventaristas
    PUT /api/users/:id/block
    """
    if request.user.user_type != 'inventarista':
        return Response({
            'success': False,
            'message': 'No tienes permisos para esta acción'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(pk=pk, account=request.user.account)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    user.is_blocked = request.data.get('is_blocked', False)
    user.blocked_reason = request.data.get('blocked_reason', '')
    user.blocked_until = request.data.get('blocked_until', None)
    user.save()
    
    return Response({
        'success': True,
        'message': f"Usuario {'bloqueado' if user.is_blocked else 'desbloqueado'} exitosamente",
        'data': UserSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_employee_view(request):
    """
    Auto-registro de empleado usando el código de empresa
    POST /api/auth/register-employee/
    Body: { email, password, full_name, company_code }
    """
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')
    full_name = request.data.get('full_name', '').strip()
    company_code = request.data.get('company_code', '').strip().upper()

    errors = {}
    if not email:
        errors['email'] = ['El email es obligatorio']
    if not password or len(password) < 6:
        errors['password'] = ['La contraseña debe tener al menos 6 caracteres']
    if not full_name:
        errors['full_name'] = ['El nombre completo es obligatorio']
    if not company_code:
        errors['company_code'] = ['El código de empresa es obligatorio']
    if errors:
        return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        account = Account.objects.get(company_code=company_code, is_active=True)
    except Account.DoesNotExist:
        return Response({
            'success': False,
            'errors': {'company_code': ['Código de empresa inválido o cuenta inactiva']}
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'errors': {'email': ['Ya existe una cuenta con este email']}
        }, status=status.HTTP_400_BAD_REQUEST)

    current_users = User.objects.filter(account=account).count()
    if account.max_users != -1 and current_users >= account.max_users:
        return Response({
            'success': False,
            'errors': {'company_code': ['La cuenta ha alcanzado el límite de usuarios de su plan']}
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        user_type='employee',
        account=account,
    )
    refresh = RefreshToken.for_user(user)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    return Response({
        'success': True,
        'message': f'Cuenta creada en {account.company_name}',
        'data': {
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Cambiar contraseña del usuario autenticado
    POST /api/auth/change-password/
    Body: {current_password, new_password}
    """
    user = request.user
    current_password = request.data.get('current_password', '')
    new_password = request.data.get('new_password', '')

    if not current_password or not new_password:
        return Response({
            'success': False,
            'error': 'Se requieren current_password y new_password'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(current_password):
        return Response({
            'success': False,
            'error': 'La contraseña actual es incorrecta'
        }, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 6:
        return Response({
            'success': False,
            'error': 'La nueva contraseña debe tener al menos 6 caracteres'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({
        'success': True,
        'message': 'Contraseña actualizada exitosamente'
    }, status=status.HTTP_200_OK)


# Importaciones faltantes
from rest_framework.exceptions import PermissionDenied, ValidationError
