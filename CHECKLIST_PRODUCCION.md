# Checklist de Produccion - Pack-a-Stock Backend

## ANTES DE SUBIR A LA NUBE - VERIFICACION OBLIGATORIA

### 1. Seguridad Critica

- [ ] Cambiar SECRET_KEY (generar uno nuevo)
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] Cambiar credenciales de superadmin
  - Email por defecto: `admin`
  - Password por defecto: `12345`
  - CAMBIAR INMEDIATAMENTE en produccion

- [ ] Configurar DEBUG=False en .env de produccion

- [ ] Configurar ALLOWED_HOSTS con tu dominio real

- [ ] Configurar CORS_ALLOWED_ORIGINS solo con dominios permitidos

### 2. Base de Datos

- [ ] PostgreSQL configurado y accesible
- [ ] DATABASE_URL correctamente formateada
  ```
  postgresql://usuario:password@host:5432/nombre_db
  ```
- [ ] Backups automaticos configurados

### 3. Archivos Media (AWS S3)

- [ ] Bucket S3 creado (nombre sugerido: pack-a-stock-media-prod)
- [ ] AWS_ACCESS_KEY_ID configurado
- [ ] AWS_SECRET_ACCESS_KEY configurado
- [ ] CORS configurado en el bucket
- [ ] Permisos IAM correctos

### 4. Migraciones

- [ ] Todas las migraciones aplicadas
  ```bash
  python manage.py showmigrations
  ```
- [ ] Verificar que no hay migraciones pendientes

### 5. Archivos Estaticos

- [ ] collectstatic ejecutado
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] WhiteNoise configurado (ya incluido en settings.py)

### 6. Variables de Entorno

Copiar `.env.production` y configurar TODAS estas variables:

```bash
SECRET_KEY=<GENERAR-NUEVO>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://usuario:password@host:5432/db
CORS_ALLOWED_ORIGINS=https://tu-frontend.com
AWS_ACCESS_KEY_ID=<TU-KEY>
AWS_SECRET_ACCESS_KEY=<TU-SECRET>
AWS_STORAGE_BUCKET_NAME=pack-a-stock-media-prod
AWS_S3_REGION_NAME=us-east-1
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### 7. Dependencias

- [ ] requirements.txt actualizado
- [ ] Todas las dependencias instalables en produccion
  ```bash
  pip install -r requirements.txt
  ```

### 8. Configuracion del Servidor

- [ ] Procfile creado (Railway, Render, Heroku)
- [ ] runtime.txt con Python 3.13.1
- [ ] Gunicorn configurado como servidor WSGI
- [ ] Logs configurados y accesibles

### 9. Testing Pre-Deployment

- [ ] Servidor local funciona correctamente
  ```bash
  python manage.py runserver
  ```
- [ ] Admin panel accesible en /admin/
- [ ] Login funciona
- [ ] API endpoints responden
- [ ] No errores en consola

### 10. Post-Deployment

Despues de subir:

- [ ] Crear nuevo superadmin en produccion
  ```bash
  python manage.py create_superadmin
  ```
- [ ] Cambiar credenciales default
- [ ] Probar login en produccion
- [ ] Verificar que archivos media se suben a S3
- [ ] Verificar logs de errores
- [ ] Probar creacion de QR codes

## Plataformas Recomendadas

### Railway (Mas facil)
- Deploy automatico desde GitHub
- PostgreSQL incluido gratis
- Variables de entorno en dashboard
- SSL automatico

### Render
- Deploy automatico desde GitHub
- PostgreSQL gratis (limitado)
- Variables de entorno en dashboard
- SSL automatico

### IONOS (Mas control)
- VPS con control total
- Requiere configuracion manual
- Nginx + Gunicorn
- Mejor para produccion a gran escala

## Comandos de Deployment

### Railway
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Render
- Conectar repo en dashboard
- Build: `pip install -r requirements.txt`
- Start: `gunicorn pack_a_stock_api.wsgi`

### Manual (VPS/IONOS)
```bash
git clone <repo>
cd Pack-a-Stock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.production .env
# Editar .env con valores reales
python manage.py migrate
python manage.py create_superadmin
python manage.py collectstatic --noinput
gunicorn pack_a_stock_api.wsgi
```

## Verificacion Post-Deployment

```bash
# Probar health check
curl https://tu-dominio.com/admin/

# Verificar SSL
curl -I https://tu-dominio.com

# Ver logs
railway logs  # Railway
render logs   # Render
tail -f logs/django.log  # Manual
```

## Problemas Comunes

### "DisallowedHost at /"
**Solucion:** Agregar dominio a ALLOWED_HOSTS

### "CORS error from frontend"
**Solucion:** Agregar frontend URL a CORS_ALLOWED_ORIGINS

### "Database connection failed"
**Solucion:** Verificar DATABASE_URL y que PostgreSQL esta corriendo

### "Static files 404"
**Solucion:** Ejecutar collectstatic, verificar WhiteNoise

### "Media files 404"
**Solucion:** Verificar AWS S3 credentials y permisos

## Soporte

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guia completa
- [BACKEND_DOCS.md](BACKEND_DOCS.md) - Documentacion tecnica
- [README.md](README.md) - Inicio rapido
