# 📦 Pack-a-Stock Backend API

Sistema SaaS multi-tenant de gestión de inventarios y préstamos de materiales empresariales.

![Django](https://img.shields.io/badge/Django-5.2-green)
![DRF](https://img.shields.io/badge/DRF-3.14-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🎯 Descripción

Backend API REST para Pack-a-Stock, un sistema que permite a empresas gestionar inventarios de materiales y controlar préstamos a empleados.

**Características principales:**
- 🏢 Multi-tenant (cada empresa tiene datos aislados)
- 🔐 Autenticación JWT
- 📦 Gestión de materiales (consumibles y no consumibles)
- 📋 Sistema de solicitudes y préstamos
- 🏷️ Generación de códigos QR
- 📊 Auditoría completa
- 🔒 Seguridad avanzada

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 2. Levantar servicios
docker compose up --build

# 3. Crear superusuario (en otra terminal)
docker compose exec backend python manage.py createsuperuser

# 4. Acceder a la API
# http://localhost:8000/api/
```

**Script automático (Windows):**
```powershell
.\setup.ps1
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Editar valores

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Crear superadmin
python manage.py create_superadmin

# 6. Ejecutar servidor
python manage.py runserver
# http://localhost:8000/api/
```

## 📋 Requisitos

- Python 3.12+
- PostgreSQL 16+ (o SQLite para desarrollo)
- Docker y Docker Compose (opcional)

## 🏗️ Arquitectura del Proyecto

```
Pack-a-Stock/                    # BACKEND (Django + DRF)
├── accounts/                    # Autenticación y usuarios
├── materials/                   # Gestión de materiales
├── loans/                       # Préstamos y solicitudes
├── audit/                       # Auditoría
├── labels/                      # Generación de QR
├── pack_a_stock_api/           # Configuración Django
├── docker-compose.yml          # Docker desarrollo
├── docker-compose.prod.yml     # Docker producción
├── Dockerfile                  # Imagen Docker
├── entrypoint.sh              # Script de inicio
└── .env.example               # Plantilla de variables

Frontend (separado):
└── Front_End_SaaS/            # Next.js + React (ver repo)
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=packastock_db
DB_USER=packastock_user
DB_PASSWORD=tu-password
DB_HOST=db  # 'db' para Docker, 'localhost' para local
DB_PORT=5432

# JWT
JWT_SECRET_KEY=tu-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Ver .env.example para todas las variables
```

**Generar SECRET_KEY seguro:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 📊 Estado del Proyecto

**Versión:** 1.0.0  
**Estado:** ✅ Backend completo - Frontend en desarrollo  
**Última actualización:** 4 de Febrero, 2026

### Completado ✅
- [x] 11/11 Modelos de base de datos
- [x] API REST completa (DRF)
- [x] Autenticación JWT
- [x] Multi-tenancy implementado
- [x] Sistema de auditoría
- [x] Generación de QR codes
- [x] Docker configurado
- [x] Variables de entorno
- [x] Guías de deployment

### En Desarrollo 🚧
- [ ] Frontend Web (Next.js)
- [ ] App Móvil (React Native/Flutter)
- [ ] Push Notifications
- [ ] Tests automatizados

## 📚 Documentación

- **[PLAN_DESARROLLO.md](PLAN_DESARROLLO.md)** - Plan completo del sistema
- **[BACKEND_DOCS.md](BACKEND_DOCS.md)** - Documentación técnica de la API
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guía de deployment
- **[SETUP_COMPLETO.md](SETUP_COMPLETO.md)** - Resumen de configuración
- **[Documentacion/](Documentacion/)** - Documentación adicional

## 🐳 Docker

### Desarrollo

```bash
docker compose up --build
# API: http://localhost:8000/api/
# PostgreSQL: localhost:5432
```

### Producción

```bash
docker compose -f docker-compose.prod.yml up -d --build
# Incluye Nginx como reverse proxy
# SSL/HTTPS configurado
```

## 🔗 API Endpoints

### Autenticación
```
POST   /api/auth/login/           # Login (JWT)
POST   /api/auth/refresh/         # Refresh token
POST   /api/auth/register/        # Registro
```

### Materiales
```
GET    /api/materials/            # Listar materiales
POST   /api/materials/            # Crear material
GET    /api/materials/{id}/       # Detalle
PUT    /api/materials/{id}/       # Actualizar
DELETE /api/materials/{id}/       # Eliminar
GET    /api/materials/available/  # Disponibles

GET    /api/categories/           # Categorías
GET    /api/locations/            # Ubicaciones
```

### Préstamos
```
GET    /api/loan-requests/        # Solicitudes
POST   /api/loan-requests/        # Crear solicitud
PUT    /api/loan-requests/{id}/   # Aprobar/Rechazar

GET    /api/loans/                # Préstamos activos
POST   /api/loans/                # Registrar entrega
PUT    /api/loans/{id}/return/    # Registrar devolución

POST   /api/loan-extensions/      # Solicitar extensión
```

Ver [BACKEND_DOCS.md](BACKEND_DOCS.md) para endpoints completos.

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

**Estado de tests:**
- ✅ Modelos: 11/11 validados
- ⏳ API Endpoints: En desarrollo
- ⏳ Integración: Pendiente

## 🔒 Seguridad

- JWT Authentication con refresh tokens
- CORS configurado
- Rate limiting implementado
- HTTPS/SSL en producción
- Headers de seguridad (HSTS, XSS Protection)
- Multi-tenancy con aislamiento de datos
- Auditoría completa de acciones

## 🚀 Deployment

### VPS/Servidor Propio

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/Pack-a-Stock.git
cd Pack-a-Stock

# 2. Configurar .env
cp .env.example .env
nano .env  # Editar valores de producción

# 3. Levantar con Docker
docker compose -f docker-compose.prod.yml up -d --build

# 4. SSL con Let's Encrypt
sudo certbot --nginx -d api.tudominio.com
```

Ver [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) para guía completa.

### Servicios Cloud

- **Railway/Render:** Conectar repositorio GitHub
- **Heroku:** Usar Procfile incluido
- **AWS/DigitalOcean:** Docker Compose

## 🛠️ Comandos Útiles

```bash
# Docker
docker compose logs -f backend        # Ver logs
docker compose exec backend bash      # Entrar al contenedor
docker compose restart backend        # Reiniciar
docker compose down -v                # Detener y limpiar

# Django
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic

# Base de datos (backup)
docker compose exec db pg_dump -U packastock_user packastock_db > backup.sql

# Restaurar
docker compose exec -T db psql -U packastock_user packastock_db < backup.sql
```

## 📱 Integración Móvil

El backend está preparado para servir tanto al frontend web como a la app móvil:

- Mismos endpoints JWT
- CORS configurado para móvil
- Push notifications ready (FCM)
- Endpoints optimizados para móvil

## 🤝 Contribuir

Este es un proyecto privado. Contacta al administrador para contribuir.

## 📝 Licencia

Privado - Pack-a-Stock © 2026

## 📞 Soporte

Para problemas o dudas:
1. Revisar documentación
2. Verificar logs: `docker compose logs backend`
3. Consultar [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Desarrollado con ❤️ para gestión eficiente de inventarios**


- 11 modelos probados (100%)
- 11 metodos probados (100%)
- Validaciones verificadas
- Relaciones confirmadas
- Auditoria implementada

Ver resultados completos en BACKEND_DOCS.md

## Deployment a Produccion

Antes de subir a la nube, asegurate de:

1. Configurar variables de entorno en `.env.production`
2. Cambiar SECRET_KEY y credenciales de admin
3. Configurar PostgreSQL y AWS S3
4. Revisar [DEPLOYMENT.md](DEPLOYMENT.md) para guia completa

**Archivos criticos:**
- `Procfile` - Comandos para Railway/Render/Heroku
- `runtime.txt` - Version de Python
- `.env.production` - Variables de entorno de produccion
- `DEPLOYMENT.md` - Guia completa de deployment

## Comandos Utiles

```bash
# Crear superadmin
python manage.py create_superadmin

# Ejecutar migraciones
python manage.py migrate

# Crear nuevas migraciones
python manage.py makemigrations

# Abrir shell de Django
python manage.py shell

# Ejecutar tests
python manage.py test

# Crear usuario normal
python manage.py createsuperuser
```

## API Endpoints

(En desarrollo - proximamente en BACKEND_DOCS.md)

```
/api/accounts/
/api/materials/
/api/loans/
/api/auth/token/
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Privado

## Contacto

Ernesto Garcia Valenzuela
Gabriel Armando Gomez Ramirez
Jaime Issac Lopex Guerrero
Yael Contreras Rios
Carlos Alexis Ruelas Gonzalez

---

**Documentacion completa:** [BACKEND_DOCS.md](BACKEND_DOCS.md)
