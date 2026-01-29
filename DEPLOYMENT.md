# Guia de Despliegue a Produccion - Pack-a-Stock Backend

## Pre-requisitos

- Cuenta en plataforma de hosting (Railway, Render, IONOS, AWS, etc.)
- Base de datos PostgreSQL
- Bucket S3 de AWS (para archivos media)
- Dominio (opcional pero recomendado)

## Pasos para Deployment

### 1. Preparar Variables de Entorno

Copia `.env.production` y configura las siguientes variables OBLIGATORIAS:

```bash
SECRET_KEY=genera-una-clave-secreta-unica-aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://usuario:password@host:5432/db_name
CORS_ALLOWED_ORIGINS=https://tu-frontend.com
AWS_ACCESS_KEY_ID=tu-aws-key
AWS_SECRET_ACCESS_KEY=tu-aws-secret
AWS_STORAGE_BUCKET_NAME=tu-bucket-name
```

**Generar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Configurar Base de Datos PostgreSQL

**IONOS:**
- Panel de control > Bases de datos > Crear PostgreSQL
- Copia el DATABASE_URL completo

**Railway/Render:**
- Agregar servicio PostgreSQL
- Copiar variable DATABASE_URL automaticamente

### 3. Configurar AWS S3 para Archivos Media

1. Crear bucket en S3 (nombre: `pack-a-stock-media-prod`)
2. Configurar CORS en el bucket:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```
3. Crear usuario IAM con permisos S3
4. Copiar Access Key ID y Secret Access Key

### 4. Deployment en Railway (Recomendado)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Agregar variables de entorno
railway variables set SECRET_KEY="tu-secret-key"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS="*.railway.app"
railway variables set DATABASE_URL="postgresql://..."
railway variables set AWS_ACCESS_KEY_ID="..."
railway variables set AWS_SECRET_ACCESS_KEY="..."
railway variables set AWS_STORAGE_BUCKET_NAME="pack-a-stock-media-prod"

# Deploy
railway up
```

### 5. Deployment en Render

1. Conectar repositorio GitHub
2. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn pack_a_stock_api.wsgi`
3. Agregar variables de entorno desde el dashboard
4. Crear PostgreSQL database (automatico)
5. Deploy

### 6. Deployment en IONOS (VPS/Shared Hosting)

```bash
# SSH al servidor
ssh usuario@tu-servidor.com

# Clonar repositorio
git clone <tu-repo>
cd Pack-a-Stock

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.production .env
nano .env  # Editar con valores reales

# Ejecutar migraciones
python manage.py migrate

# Crear superadmin
python manage.py create_superadmin

# Recolectar archivos estaticos
python manage.py collectstatic --noinput

# Configurar Gunicorn + Nginx
# Ver seccion Configuracion Nginx abajo
```

### 7. Post-Deployment

```bash
# Verificar migraciones
python manage.py showmigrations

# Crear superadmin
python manage.py create_superadmin

# Verificar que todo funciona
curl https://tu-dominio.com/admin/
```

## Configuracion Nginx (para VPS)

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /ruta/a/Pack-a-Stock/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuracion Gunicorn Service (systemd)

```ini
[Unit]
Description=Pack-a-Stock Gunicorn daemon
After=network.target

[Service]
User=tu-usuario
Group=www-data
WorkingDirectory=/ruta/a/Pack-a-Stock
ExecStart=/ruta/a/Pack-a-Stock/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          pack_a_stock_api.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start packastock
sudo systemctl enable packastock
```

## Configuracion Celery (opcional)

Si usas tareas asincronas:

```bash
# Worker
celery -A pack_a_stock_api worker --loglevel=info

# Beat (tareas programadas)
celery -A pack_a_stock_api beat --loglevel=info
```

## Checklist de Seguridad

- [ ] SECRET_KEY cambiado y unico
- [ ] DEBUG=False en produccion
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] HTTPS habilitado (SSL/TLS)
- [ ] CORS_ALLOWED_ORIGINS solo dominios permitidos
- [ ] Credenciales de superadmin cambiadas
- [ ] AWS S3 bucket privado con politicas correctas
- [ ] Database backups configurados
- [ ] Logs configurados y monitoreados
- [ ] Rate limiting implementado (opcional)

## Comandos Utiles

```bash
# Ver logs en Railway
railway logs

# Ver logs en Render
render logs

# Ver logs en servidor
tail -f logs/django.log

# Reiniciar servicio
sudo systemctl restart packastock

# Actualizar codigo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart packastock
```

## Troubleshooting

### Error: "DisallowedHost"
- Verificar ALLOWED_HOSTS en .env
- Asegurar que incluye el dominio exacto

### Error: "No module named 'pack_a_stock_api'"
- Verificar PYTHONPATH
- Reiniciar servidor

### Error: "Database connection failed"
- Verificar DATABASE_URL
- Confirmar que PostgreSQL esta corriendo
- Verificar firewall/security groups

### Archivos media no se muestran
- Verificar AWS credentials
- Confirmar permisos del bucket S3
- Revisar CORS del bucket

## Soporte

Para mas informacion consultar:
- [BACKEND_DOCS.md](BACKEND_DOCS.md) - Documentacion completa
- [README.md](README.md) - Guia de inicio rapido
