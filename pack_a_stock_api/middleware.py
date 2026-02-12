"""
Middleware personalizado para seguridad adicional
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Agrega headers de seguridad adicionales a todas las respuestas
    """
    def process_response(self, request, response):
        # Prevenir clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevenir MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (antes Feature Policy)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        if not request.path.startswith('/admin/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self';"
            )
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Registra requests sospechosos y eventos de seguridad
    """
    def process_request(self, request):
        # Log de intentos de acceso no autorizados
        if request.path.startswith('/admin/') and not request.user.is_authenticated:
            logger.warning(
                f"Intento de acceso no autenticado a admin desde {self.get_client_ip(request)} - {request.path}"
            )
        
        # Log de métodos sospechosos
        if request.method in ['TRACE', 'TRACK']:
            logger.warning(
                f"Método HTTP sospechoso {request.method} desde {self.get_client_ip(request)}"
            )
            return HttpResponseForbidden("Método no permitido")
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
