"""
Permisos personalizados para Pack-a-Stock API
"""
from rest_framework import permissions


class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Permiso para super usuarios o administradores de cuenta
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.user_type in ['admin', 'super_admin']
        )


class IsSameAccountOrReadOnly(permissions.BasePermission):
    """
    Permite edición solo si pertenece a la misma cuenta
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Edición solo si es de la misma cuenta
        if hasattr(obj, 'account'):
            return obj.account == request.user.account
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso solo al dueño del recurso o admin
    """
    def has_object_permission(self, request, view, obj):
        # Superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return True
        
        # Admins de la cuenta tienen acceso
        if request.user.user_type in ['admin', 'super_admin']:
            return True
        
        # Dueño del recurso
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'borrower'):
            return obj.borrower == request.user
        
        return False


class CanManageUsers(permissions.BasePermission):
    """
    Solo administradores pueden gestionar usuarios
    """
    def has_permission(self, request, view):
        # GET permitido para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Crear/Modificar/Eliminar solo para admins
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.user_type in ['admin', 'super_admin']
        )
