#!/bin/bash

# ========================================
# ENTRYPOINT SCRIPT PARA DOCKER
# ========================================
# Este script se ejecuta al iniciar el contenedor Docker
# Espera a que PostgreSQL esté listo antes de ejecutar comandos

set -e

echo "========================================="
echo "🚀 Pack-a-Stock - Iniciando aplicación..."
echo "========================================="

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "   PostgreSQL no está disponible aún - esperando..."
  sleep 2
done

echo "✅ PostgreSQL está listo!"

# Ejecutar migraciones
echo "📊 Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario por defecto si no existe
echo "👤 Verificando superusuario..."
python manage.py create_superadmin || true

echo "========================================="
echo "✅ Configuración completada!"
echo "🎯 Iniciando servidor Django..."
echo "========================================="

# Ejecutar el comando principal (CMD del Dockerfile)
exec "$@"
