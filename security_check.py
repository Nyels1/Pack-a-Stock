"""
Script de Verificación de Seguridad - Pack-a-Stock API
Ejecutar: python security_check.py
"""
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pack_a_stock_api.settings')

import django
django.setup()

from django.conf import settings
from rest_framework import status


def check_security():
    """Verifica configuraciones de seguridad"""
    
    print("=" * 60)
    print("🔒 PACK-A-STOCK API - ANÁLISIS DE SEGURIDAD")
    print("=" * 60)
    print()
    
    score = 0
    max_score = 0
    
    # 1. DEBUG Mode
    max_score += 10
    print("1. DEBUG Mode:")
    if not settings.DEBUG:
        print("   ✅ DEBUG=False (Producción seguro) [+10 pts]")
        score += 10
    else:
        print("   ⚠️  DEBUG=True (Solo desarrollo) [+0 pts]")
    print()
    
    # 2. SECRET_KEY
    max_score += 10
    print("2. SECRET_KEY:")
    if len(settings.SECRET_KEY) >= 50:
        print(f"   ✅ SECRET_KEY fuerte ({len(settings.SECRET_KEY)} caracteres) [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  SECRET_KEY débil ({len(settings.SECRET_KEY)} caracteres) [+5 pts]")
        score += 5
    print()
    
    # 3. ALLOWED_HOSTS
    max_score += 10
    print("3. ALLOWED_HOSTS:")
    if '*' not in settings.ALLOWED_HOSTS:
        print(f"   ✅ ALLOWED_HOSTS específico: {settings.ALLOWED_HOSTS} [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  ALLOWED_HOSTS abierto (solo desarrollo) [+0 pts]")
    print()
    
    # 4. HTTPS Settings
    max_score += 10
    print("4. HTTPS/SSL Configuration:")
    https_checks = 0
    if hasattr(settings, 'SECURE_SSL_REDIRECT'):
        if not settings.DEBUG and settings.SECURE_SSL_REDIRECT:
            https_checks += 1
    if hasattr(settings, 'SECURE_HSTS_SECONDS'):
        if settings.SECURE_HSTS_SECONDS > 0:
            https_checks += 1
    if hasattr(settings, 'SESSION_COOKIE_SECURE'):
        if not settings.DEBUG and settings.SESSION_COOKIE_SECURE:
            https_checks += 1
    
    if https_checks >= 3:
        print(f"   ✅ HTTPS configurado correctamente [+10 pts]")
        score += 10
    elif https_checks >= 2:
        print(f"   ⚠️  HTTPS parcialmente configurado [+7 pts]")
        score += 7
    else:
        print(f"   ⚠️  HTTPS no configurado (modo desarrollo) [+3 pts]")
        score += 3
    print()
    
    # 5. JWT Settings
    max_score += 10
    print("5. JWT Configuration:")
    jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
    access_lifetime = jwt_settings.get('ACCESS_TOKEN_LIFETIME')
    if access_lifetime and access_lifetime.total_seconds() <= 3600:  # <= 60 min
        print(f"   ✅ Access token lifetime seguro ({access_lifetime.total_seconds()/60} min) [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  Access token lifetime largo [+5 pts]")
        score += 5
    print()
    
    # 6. Rate Limiting
    max_score += 10
    print("6. Rate Limiting (Throttling):")
    rest_settings = getattr(settings, 'REST_FRAMEWORK', {})
    if 'DEFAULT_THROTTLE_CLASSES' in rest_settings:
        print(f"   ✅ Throttling configurado [+10 pts]")
        print(f"   Rates: {rest_settings.get('DEFAULT_THROTTLE_RATES', {})}")
        score += 10
    else:
        print(f"   ❌ Throttling no configurado [+0 pts]")
    print()
    
    # 7. CORS Configuration
    max_score += 10
    print("7. CORS Configuration:")
    cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
    if cors_origins and ('*' not in str(cors_origins)):
        print(f"   ✅ CORS específico: {len(cors_origins)} orígenes [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  CORS abierto o no configurado [+5 pts]")
        score += 5
    print()
    
    # 8. Password Validation
    max_score += 10
    print("8. Password Validators:")
    validators = settings.AUTH_PASSWORD_VALIDATORS
    if len(validators) >= 4:
        print(f"   ✅ {len(validators)} validadores configurados [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  Solo {len(validators)} validadores [+5 pts]")
        score += 5
    print()
    
    # 9. Security Headers
    max_score += 10
    print("9. Security Headers Middleware:")
    middleware = settings.MIDDLEWARE
    security_middleware = [m for m in middleware if 'Security' in m or 'security' in m]
    if len(security_middleware) >= 2:
        print(f"   ✅ Security middleware configurado [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  Security middleware básico [+7 pts]")
        score += 7
    print()
    
    # 10. Database Security
    max_score += 10
    print("10. Database Configuration:")
    db_config = settings.DATABASES.get('default', {})
    if db_config.get('ENGINE') == 'django.db.backends.postgresql':
        print(f"   ✅ PostgreSQL (recomendado) [+10 pts]")
        score += 10
    else:
        print(f"   ⚠️  Otra base de datos [+5 pts]")
        score += 5
    print()
    
    # Resultado Final
    print("=" * 60)
    percentage = (score / max_score) * 10
    print(f"📊 PUNTUACIÓN FINAL: {percentage:.1f}/10")
    print(f"   Puntos: {score}/{max_score}")
    print("=" * 60)
    print()
    
    # Interpretación
    if percentage >= 9:
        print("🌟 EXCELENTE - Seguridad de nivel empresarial")
    elif percentage >= 8:
        print("✅ MUY BUENO - Seguridad robusta")
    elif percentage >= 7:
        print("👍 BUENO - Seguridad adecuada para producción")
    elif percentage >= 6:
        print("⚠️  ACEPTABLE - Mejorar antes de producción")
    else:
        print("❌ INSUFICIENTE - Requiere mejoras urgentes")
    print()
    
    # Recomendaciones
    print("=" * 60)
    print("💡 RECOMENDACIONES ESPECÍFICAS:")
    print("=" * 60)
    
    if settings.DEBUG:
        print("1. ⚠️  Configurar DEBUG=False en producción")
    
    if '*' in settings.ALLOWED_HOSTS:
        print("2. ⚠️  Configurar ALLOWED_HOSTS específico")
    
    if len(settings.SECRET_KEY) < 50:
        print("3. ⚠️  Generar SECRET_KEY más fuerte")
    
    if 'DEFAULT_THROTTLE_CLASSES' not in rest_settings:
        print("4. ⚠️  Implementar rate limiting")
    
    print()
    print("=" * 60)
    print("✅ Análisis completado")
    print("=" * 60)
    
    return percentage


if __name__ == '__main__':
    try:
        check_security()
    except Exception as e:
        print(f"❌ Error al ejecutar análisis: {e}")
        import traceback
        traceback.print_exc()
