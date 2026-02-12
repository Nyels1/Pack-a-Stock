"""
Generador de SECRET_KEY seguro para Django
Ejecutar: python generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

print("=" * 60)
print("🔐 GENERADOR DE SECRET_KEY SEGURO")
print("=" * 60)
print()
print("Copia esta SECRET_KEY a tu archivo .env de producción:")
print()
print("-" * 60)
secret_key = get_random_secret_key()
print(secret_key)
print("-" * 60)
print()
print(f"✅ Longitud: {len(secret_key)} caracteres")
print()
print("⚠️  IMPORTANTE:")
print("1. Nunca compartir esta clave")
print("2. Usar diferente clave en desarrollo y producción")
print("3. Guardar en lugar seguro (backup)")
print()
print("=" * 60)
