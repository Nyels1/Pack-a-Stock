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
        if account.subscription_plan == 'freemium':
            msg = (
                f'Tu administrador no cuenta con un plan avanzado. '
                f'El plan gratuito solo permite {account.max_users} usuarios. '
                f'Pide a tu administrador que actualice su suscripción.'
            )
        else:
            msg = (
                f'La empresa ha alcanzado el límite de su plan '
                f'({account.max_users} usuarios). Contacta a tu administrador.'
            )
        return Response({
            'success': False,
            'message': msg,
            'errors': {'company_code': [msg]}
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


# ─── Firebase Auth ────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def check_auth_method_view(request):
    """
    Verifica si un email usa Google Sign-In.
    POST /api/auth/check-method/
    Body: { email: str }
    """
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({'success': False, 'message': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'success': True, 'exists': False})

    return Response({
        'success': True,
        'exists': True,
        'uses_google': bool(user.firebase_uid),
    })


def _init_firebase():
    """Inicializa Firebase Admin SDK una sola vez."""
    import firebase_admin
    if not firebase_admin._apps:
        import os
        from django.conf import settings
        from firebase_admin import credentials as fb_credentials
        cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')
        cred = fb_credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_auth_view(request):
    """
    Login / registro mediante Firebase (Google o email/password de Firebase).
    POST /api/auth/firebase/
    Body: {
        firebase_token: str,           # ID token de Firebase (obligatorio)
        user_type: str,                # 'inventarista' | 'employee' (solo para registro)
        company_name: str,             # obligatorio si user_type='inventarista' y es nuevo
        company_code: str,             # obligatorio si user_type='employee' y es nuevo
        full_name: str,                # opcional, se toma de Firebase si no se envía
    }
    """
    import firebase_admin
    from firebase_admin import auth as fb_auth

    firebase_token = request.data.get('firebase_token', '').strip()
    if not firebase_token:
        return Response({'success': False, 'message': 'firebase_token es obligatorio'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Inicializar Firebase Admin
    try:
        _init_firebase()
    except Exception as e:
        return Response({'success': False, 'message': f'Error al inicializar Firebase: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Verificar el token con Firebase
    try:
        decoded = fb_auth.verify_id_token(firebase_token)
    except fb_auth.ExpiredIdTokenError:
        return Response({'success': False, 'message': 'Token de Firebase expirado'},
                        status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        return Response({'success': False, 'message': 'Token de Firebase inválido'},
                        status=status.HTTP_401_UNAUTHORIZED)

    firebase_uid = decoded['uid']
    email = decoded.get('email', '').lower().strip()
    firebase_name = decoded.get('name', '') or request.data.get('full_name', '')

    # ── Buscar usuario existente ──────────────────────────────────────────────
    user = User.objects.filter(firebase_uid=firebase_uid).first()

    if not user and email:
        user = User.objects.filter(email=email).first()
        if user:
            # Vincular firebase_uid al usuario existente
            user.firebase_uid = firebase_uid
            user.save(update_fields=['firebase_uid'])

    # ── Login (usuario ya existe) ─────────────────────────────────────────────
    if user:
        refresh = RefreshToken.for_user(user)
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

    # ── Registro (usuario nuevo) ──────────────────────────────────────────────
    user_type = request.data.get('user_type', '').strip()
    company_name = request.data.get('company_name', '').strip()
    company_code = request.data.get('company_code', '').strip().upper()

    if not email:
        return Response({
            'success': False,
            'message': 'La cuenta de Firebase no tiene email asociado'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not user_type:
        # No hay usuario y no se enviaron datos de registro — pedir al frontend
        return Response({
            'success': False,
            'code': 'USER_NOT_FOUND',
            'message': 'Usuario no registrado. Completa tu registro.',
            'email': email,
            'full_name': firebase_name,
        }, status=status.HTTP_404_NOT_FOUND)

    if user_type == 'inventarista':
        if not company_name:
            return Response({
                'success': False,
                'message': 'El nombre de la empresa es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Account.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Ya existe una cuenta con ese email. Intenta iniciar sesión.'
            }, status=status.HTTP_400_BAD_REQUEST)

        account = Account.objects.create(
            company_name=company_name,
            email=email,
        )
        user = User.objects.create_user(
            email=email,
            password=None,
            full_name=firebase_name or email,
            user_type='inventarista',
            account=account,
            firebase_uid=firebase_uid,
        )

    elif user_type == 'employee':
        if not company_code:
            return Response({
                'success': False,
                'code': 'NEEDS_COMPANY_CODE',
                'message': 'Se requiere el código de empresa para registrarse como empleado',
                'email': email,
                'full_name': firebase_name,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(company_code=company_code, is_active=True)
        except Account.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Código de empresa inválido o cuenta inactiva'
            }, status=status.HTTP_400_BAD_REQUEST)

        current_users = User.objects.filter(account=account).count()
        if account.max_users != -1 and current_users >= account.max_users:
            return Response({
                'success': False,
                'message': f'La empresa alcanzó el límite de {account.max_users} usuarios.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Ya existe una cuenta con ese email'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            password=None,
            full_name=firebase_name or email,
            user_type='employee',
            account=account,
            firebase_uid=firebase_uid,
        )
    else:
        return Response({
            'success': False,
            'message': 'user_type debe ser inventarista o employee'
        }, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
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
    }, status=status.HTTP_201_CREATED)
