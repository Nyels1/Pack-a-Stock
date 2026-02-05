# ========================================
# PACK-A-STOCK - GUÍA DE DEPLOYMENT
# ========================================

Este documento explica cómo desplegar Pack-a-Stock en producción.

## 📋 Tabla de Contenidos

1. [Preparación](#preparación)
2. [Backend (Django)](#backend-django)
3. [Frontend (Next.js)](#frontend-nextjs)
4. [Base de Datos](#base-de-datos)
5. [SSL/HTTPS](#sslhttps)
6. [Monitoreo](#monitoreo)

---

## 🔧 Preparación

### Requisitos del Servidor

- VPS con Ubuntu 22.04 LTS o superior
- 2 GB RAM mínimo (4 GB recomendado)
- 20 GB espacio en disco
- Docker y Docker Compose instalados
- Dominio apuntando al servidor

### Instalación de Docker

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Verificar instalación
docker --version
docker compose version
```

---

## 🖥️ Backend (Django)

### 1. Clonar Repositorio

```bash
cd /var/www
git clone https://github.com/tu-usuario/Pack-a-Stock.git
cd Pack-a-Stock
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

**Configurar en .env:**

```env
# Producción
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,api.tudominio.com

# Base de datos (usar contraseñas seguras)
DB_NAME=packastock_db
DB_USER=packastock_user
DB_PASSWORD=contraseña-muy-segura-aquí

# Secret keys (generar aleatorias)
SECRET_KEY=django-secret-key-super-larga-y-aleatoria
JWT_SECRET_KEY=jwt-secret-diferente-tambien-aleatorio

# CORS
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://app.tudominio.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# AWS S3 (opcional)
AWS_ACCESS_KEY_ID=tu-key
AWS_SECRET_ACCESS_KEY=tu-secret
AWS_STORAGE_BUCKET_NAME=packastock-media
```

**Generar SECRET_KEY seguro:**

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Construir y Levantar Contenedores

```bash
# Desarrollo
docker compose up -d --build

# Producción
docker compose -f docker-compose.prod.yml up -d --build
```

### 4. Verificar Logs

```bash
docker compose logs -f backend
```

### 5. Crear Superusuario

```bash
docker compose exec backend python manage.py createsuperuser
```

### 6. Probar API

```bash
curl http://localhost:8000/api/health/
```

---

## 🌐 Frontend (Next.js)

### Opción A: Desplegar en Vercel (Recomendado)

```bash
cd Front_End_SaaS

# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Desplegar
vercel --prod
```

**Configurar en Vercel Dashboard:**
- Variables de entorno: `NEXT_PUBLIC_API_URL=https://api.tudominio.com`

### Opción B: Docker en VPS

```bash
cd Front_End_SaaS

# Crear .env.production
cp .env.example .env.production
nano .env.production
```

```env
NEXT_PUBLIC_API_URL=https://api.tudominio.com
NODE_ENV=production
```

```bash
# Build
docker build --build-arg NEXT_PUBLIC_API_URL=https://api.tudominio.com -t packastock-frontend .

# Run
docker run -d -p 3000:3000 --name frontend packastock-frontend
```

---

## 🗄️ Base de Datos

### Backups Automáticos

Crear script de backup:

```bash
nano /var/www/Pack-a-Stock/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/www/Pack-a-Stock/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="packastock_backup_$TIMESTAMP.sql"

docker compose exec -T db pg_dump -U packastock_user packastock_db > "$BACKUP_DIR/$FILENAME"

# Mantener solo últimos 7 días
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completado: $FILENAME"
```

```bash
chmod +x backup.sh

# Programar con cron (diario a las 2 AM)
crontab -e
0 2 * * * /var/www/Pack-a-Stock/backup.sh
```

### Restaurar Backup

```bash
docker compose exec -T db psql -U packastock_user packastock_db < backups/packastock_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔒 SSL/HTTPS

### Configurar Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d tudominio.com -d www.tudominio.com -d api.tudominio.com

# Renovación automática (ya configurada por defecto)
sudo certbot renew --dry-run
```

### Configurar Nginx

El archivo `nginx/nginx.conf` ya está configurado para SSL.

Copiar certificados a la ubicación esperada:

```bash
mkdir -p /var/www/Pack-a-Stock/nginx/ssl
sudo cp /etc/letsencrypt/live/tudominio.com/fullchain.pem /var/www/Pack-a-Stock/nginx/ssl/
sudo cp /etc/letsencrypt/live/tudominio.com/privkey.pem /var/www/Pack-a-Stock/nginx/ssl/
```

---

## 📊 Monitoreo

### Logs

```bash
# Backend
docker compose logs -f backend

# Base de datos
docker compose logs -f db

# Nginx
docker compose logs -f nginx

# Todos
docker compose logs -f
```

### Verificar Estado de Contenedores

```bash
docker compose ps
```

### Recursos del Sistema

```bash
# CPU y Memoria
docker stats

# Espacio en disco
df -h
du -sh /var/www/Pack-a-Stock/media/
```

---

## 🚀 Actualizar Aplicación

### Backend

```bash
cd /var/www/Pack-a-Stock

# Hacer backup antes
./backup.sh

# Obtener cambios
git pull origin main

# Reconstruir
docker compose down
docker compose up -d --build

# Ejecutar migraciones si hay
docker compose exec backend python manage.py migrate
```

### Frontend (Vercel)

```bash
# Push a GitHub (deploy automático)
git push origin main

# O manual
cd Front_End_SaaS
vercel --prod
```

---

## ⚠️ Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
docker compose logs backend

# Verificar variables de entorno
docker compose exec backend env

# Reconstruir desde cero
docker compose down -v
docker compose up --build
```

### Error de conexión a BD

```bash
# Verificar que PostgreSQL está corriendo
docker compose ps db

# Probar conexión
docker compose exec db psql -U packastock_user -d packastock_db -c "SELECT 1;"
```

### CORS Errors

Verificar en `.env`:
```env
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://app.tudominio.com
```

Debe coincidir con la URL del frontend.

---

## 📞 Soporte

Para problemas o dudas, revisar logs y documentación del proyecto.

**Comandos útiles:**

```bash
# Reiniciar todos los servicios
docker compose restart

# Detener y limpiar todo
docker compose down -v

# Ver uso de recursos
docker stats

# Entrar a un contenedor
docker compose exec backend bash
```

---

**Última actualización:** Febrero 2026
