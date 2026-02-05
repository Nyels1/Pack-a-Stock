# PLAN DE DESARROLLO - PACK-A-STOCK (SISTEMA COMPLETO)

## ARQUITECTURA DEL SISTEMA

Pack-a-Stock es un sistema SaaS multi-tenant para gestión de inventarios y préstamos de materiales empresariales.

### 🏗️ ESTRUCTURA DEL PROYECTO

```
GitHub/
├── Pack-a-Stock/              # BACKEND (Django + DRF + PostgreSQL)
│   ├── API REST para Frontend Web y App Móvil
│   ├── Docker + docker-compose.yml
│   ├── Variables de entorno (.env)
│   └── Desplegable en dominio (producción)
│
└── Front_End_SaaS/            # FRONTEND WEB (Next.js + React)
    ├── Interfaz para INVENTARISTAS únicamente
    ├── Consume API del backend
    ├── Variables de entorno (.env.local)
    └── Desplegable en Vercel/Netlify o contenedor Docker
```

### 📱 TIPOS DE USUARIOS Y PLATAFORMAS

**INVENTARISTAS (WEB):**
- Acceso: `Front_End_SaaS` (aplicación web)
- Funciones: Administración completa del sistema
- Aprueban/rechazan solicitudes de préstamos
- Gestionan inventario, usuarios, reportes

**EMPLEADOS (MÓVIL):**
- Acceso: App Móvil nativa (React Native / Flutter - FUTURA)
- Funciones: Solicitar préstamos, ver historial, escanear QR
- NO tienen acceso a la web administrativa
- Solicitudes enviadas vía API al backend

### Modelo de Negocio
- **Multi-tenant:** Cada empresa (Account) tiene datos aislados
- **Planes:** Freemium (1 ubicación, 5 usuarios) / Premium (ilimitado)
- **Backend centralizado:** Una sola instancia sirve a todos los tenants
- **Frontend separado:** Comunicación vía API REST con JWT


### Flujo Principal
1. **Móvil:** Empleado solicita préstamo de materiales mediante app móvil → API Backend
2. **Backend:** Procesa solicitud, valida disponibilidad, almacena en BD
3. **Web:** Inventarista ve notificación, revisa solicitud y aprueba/rechaza
4. **Web:** Inventarista entrega material (escanea QR, registra firma digital)
5. **Web:** Inventarista recibe devolución (escanea QR, verifica condición, registra firma)

### 🔧 STACK TECNOLÓGICO

**BACKEND (`Pack-a-Stock/`):**
- Django 5.2 + Django REST Framework
- PostgreSQL (multi-tenant con account_id)
- JWT Authentication (Simple JWT)
- Docker + docker-compose
- Variables de entorno (`.env`)
- Almacenamiento: Media files (QR codes, imágenes)
- Deploy: Dominio propio con Docker

**FRONTEND WEB (`Front_End_SaaS/`):**
- Next.js 14+ (App Router)
- React 18 + TypeScript
- Tailwind CSS + Shadcn/ui
- TanStack Query (React Query)
- Zustand (estado global)
- Variables de entorno (`.env.local`)
- Deploy: Vercel/Netlify o Docker

**APP MÓVIL (FUTURA):**
- React Native o Flutter
- Consume misma API que frontend web
- Funciones: solicitar préstamos, ver historial, escanear QR

---

## ⚙️ CONFIGURACIÓN DE VARIABLES DE ENTORNO

### Backend (Pack-a-Stock/.env)

```env
# Django Core
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,localhost

# Database (PostgreSQL)
DB_NAME=packastock_db
DB_USER=packastock_user
DB_PASSWORD=tu-password-segura
DB_HOST=db  # 'db' en Docker, 'localhost' en local
DB_PORT=5432

# JWT Settings
JWT_SECRET_KEY=tu-jwt-secret-key-diferente
JWT_ACCESS_TOKEN_LIFETIME=60  # minutos
JWT_REFRESH_TOKEN_LIFETIME=1440  # 24 horas

# CORS (para permitir frontend)
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://app.tudominio.com,http://localhost:3000

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# Email (para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# AWS S3 (opcional, para producción)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# App Settings
APP_NAME=Pack-a-Stock
APP_URL=https://app.tudominio.com
FRONTEND_URL=https://tudominio.com
MOBILE_APP_DEEP_LINK=packastock://
```

### Frontend (Front_End_SaaS/.env.local)

```env
# API Backend
NEXT_PUBLIC_API_URL=https://api.tudominio.com
# En desarrollo: http://localhost:8000

# App Settings
NEXT_PUBLIC_APP_NAME=Pack-a-Stock
NEXT_PUBLIC_APP_VERSION=1.0.0

# Environment
NODE_ENV=production  # o development

# Analytics (opcional)
NEXT_PUBLIC_GA_ID=
NEXT_PUBLIC_SENTRY_DSN=

# Feature Flags
NEXT_PUBLIC_ENABLE_QR_SCANNER=true
NEXT_PUBLIC_ENABLE_FACIAL_AUTH=false
NEXT_PUBLIC_ENABLE_REPORTS=true
```

---

## 🐳 CONFIGURACIÓN DOCKER

### docker-compose.yml (Pack-a-Stock)

**ACTUALIZACIÓN NECESARIA para variables de entorno:**

```yaml
version: "3.9"

services:
  db:
    image: postgres:16
    container_name: pack_a_stock_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - packastock_network
    restart: unless-stopped

  backend:
    build: .
    container_name: pack_a_stock_backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn pack_a_stock_api.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - packastock_network
    restart: unless-stopped

  # Opcional: Nginx como reverse proxy
  nginx:
    image: nginx:alpine
    container_name: pack_a_stock_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - packastock_network
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  packastock_network:
    driver: bridge
```

### Dockerfile (Pack-a-Stock) - ACTUALIZADO

```dockerfile
FROM python:3.12-slim

# Prevenir escritura de archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar proyecto
COPY . .

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Script de inicio (esperar a que DB esté lista)
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "pack_a_stock_api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### entrypoint.sh (Pack-a-Stock) - NUEVO ARCHIVO

```bash
#!/bin/bash

# Esperar a que PostgreSQL esté listo
echo "Esperando a PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL iniciado"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (opcional)
python manage.py create_superadmin

echo "Iniciando servidor..."
exec "$@"
```

---

## 🚀 DEPLOYMENT EN PRODUCCIÓN

### Backend (Pack-a-Stock)

**Opción 1: VPS con Docker (Recomendado)**

```bash
# En el servidor VPS

# 1. Clonar repositorio
git clone https://github.com/tu-usuario/Pack-a-Stock.git
cd Pack-a-Stock

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con valores de producción

# 3. Construir y levantar contenedores
docker-compose up -d --build

# 4. Verificar logs
docker-compose logs -f

# 5. Acceder al backend
# http://tu-servidor:8000/api/
```

**Opción 2: Railway/Render/Heroku**
- Configurar variables de entorno en el panel
- Conectar repositorio GitHub
- Deploy automático en cada push

### Frontend (Front_End_SaaS)

**Opción 1: Vercel (Recomendado para Next.js)**

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desde Front_End_SaaS/
vercel login
vercel

# Configurar variables de entorno en Vercel dashboard
# NEXT_PUBLIC_API_URL=https://api.tudominio.com
```

**Opción 2: Docker**

```dockerfile
# Front_End_SaaS/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

---

## 📱 CONSIDERACIONES MÓVILES

### App Móvil (React Native / Flutter)

**Funcionalidades Principales:**
1. **Autenticación**
   - Login con email/password
   - JWT almacenado en secure storage

2. **Solicitar Préstamos**
   - Ver catálogo de materiales disponibles
   - Escanear QR de materiales
   - Seleccionar fechas de préstamo
   - Enviar solicitud → API

3. **Mis Préstamos**
   - Ver préstamos activos
   - Ver historial
   - Solicitar extensiones
   - Notificaciones de aprobaciones/rechazos

4. **Escaneo QR**
   - Cámara nativa
   - Verificar material antes de solicitar
   - Ver detalles del material

**API Endpoints Necesarios:**

```
POST   /api/auth/login/                    # Login empleado
POST   /api/auth/refresh/                  # Refresh token

GET    /api/materials/available/           # Materiales disponibles
GET    /api/materials/{id}/                # Detalle material
GET    /api/materials/scan/{qr_code}/      # Info por QR

POST   /api/loan-requests/                 # Crear solicitud
GET    /api/loan-requests/my-requests/     # Mis solicitudes
GET    /api/loan-requests/{id}/            # Detalle solicitud

GET    /api/loans/my-loans/                # Mis préstamos activos
POST   /api/loan-extensions/               # Solicitar extensión

GET    /api/notifications/                 # Notificaciones push
```

**Configuración Backend para Móvil:**

```python
# Pack-a-Stock/pack_a_stock_api/settings.py

INSTALLED_APPS += [
    'fcm_django',  # Firebase Cloud Messaging para push notifications
]

# CORS: Permitir app móvil
CORS_ALLOWED_ORIGINS += [
    'capacitor://localhost',  # Ionic/Capacitor
    'http://localhost',       # React Native
]

# Configurar FCM
FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": config('FCM_SERVER_KEY'),
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": True,
}
```

---

## 🔒 SEGURIDAD

### Backend

```python
# settings.py - PRODUCCIÓN

# HTTPS obligatorio
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Headers de seguridad
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS restrictivo
CORS_ALLOWED_ORIGINS = [
    'https://tudominio.com',
    'https://app.tudominio.com',
]
CORS_ALLOW_CREDENTIALS = True

# Rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### Frontend

```typescript
// Front_End_SaaS/lib/api.ts

import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Intentar refresh
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh/`,
            { refresh: refreshToken }
          )
          localStorage.setItem('access_token', data.access)
          return api.request(error.config)
        } catch {
          // Redirect a login
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

---

## TIPOS DE MATERIALES

### Materiales Regulares (No consumibles)
- Se prestan y SE DEVUELVEN
- Tienen QR individual único
- Control de estado: disponible, en préstamo, mantenimiento, dañado
- Ejemplos: laptops, proyectores, taladros, cámaras

### Materiales Consumibles
- Se entregan y NO se devuelven (se consumen)
- Manejo por stock/cantidad
- QR por lote (todas las unidades comparten el mismo QR)
- Al aprobar préstamo: se reduce stock permanentemente
- Ejemplos: tornillos, cables USB, pilas, papel

---

## ARQUITECTURA VISUAL

### Paleta de Colores Recomendada
```
Primario: #2563EB (Azul profesional - acciones principales)
Secundario: #10B981 (Verde - estados positivos/disponible)
Advertencia: #F59E0B (Amarillo - alertas stock bajo)
Peligro: #EF4444 (Rojo - vencidos/bloqueados)
Neutro: #64748B (Gris - textos secundarios)
Fondo: #F8FAFC (Gris muy claro)
Superficie: #FFFFFF (Blanco)
```

### Tipografía
- **Principal:** Inter, SF Pro, o Segoe UI
- **Monoespaciada:** JetBrains Mono (para códigos QR, SKU)

### Componentes Clave
- Tablas con paginación y filtros
- Modales para acciones rápidas
- Sidebar colapsable
- Cards para métricas
- Badges de estado (colores según estado)
- Scanner de QR integrado (cámara web)
- Área de firma digital (canvas)

---

## PÁGINAS Y VISTAS NECESARIAS

### 1. 🔐 AUTENTICACIÓN

#### Login
- Logo de Pack-a-Stock centrado
- Email + Password
- Botón "Iniciar Sesión"
- Link "¿Olvidaste tu contraseña?"
- NO hay registro público (solo para demo, luego se asignan cuentas)

#### Recuperar Contraseña
- Campo email
- Instrucciones claras
- Botón enviar link de recuperación

---

### 2. 📊 DASHBOARD PRINCIPAL

**Métricas en Cards (fila superior):**
- Total de Materiales (número grande + icono)
- Materiales Disponibles (verde)
- Materiales en Préstamo (azul)
- Préstamos Vencidos (rojo, con número destacado)
- Stock Bajo (amarillo, con número de alertas)
- Solicitudes Pendientes (naranja, requieren atención)

**Sección: Alertas Importantes (segunda fila)**
- Lista de préstamos VENCIDOS (rojo)
  - Nombre del empleado, material, días de retraso
  - Botón "Ver detalle" o "Contactar"
- Lista de materiales con STOCK BAJO (amarillo)
  - Nombre material, cantidad actual, mínimo requerido
  - Botón "Reordenar" o "Ver detalle"

**Gráficas (tercera fila)**
- Gráfica de barras: Préstamos por categoría (últimos 30 días)
- Gráfica de línea: Tendencia de préstamos (últimos 6 meses)
- Gráfica de dona: Distribución de materiales por estado

**Actividad Reciente (columna derecha o cuarta fila)**
- Timeline de últimas acciones:
  - "Juan Pérez devolvió Laptop HP #QR123" (hace 2 horas)
  - "María García solicitó Proyector Epson" (hace 5 horas)
  - "Stock de Cable USB bajo nivel mínimo" (hace 1 día)

---

### 3. 📦 GESTIÓN DE MATERIALES

#### Vista Principal: Tabla de Materiales
**Header:**
- Título "Materiales"
- Botón "+ Nuevo Material" (azul, destacado)
- Barra de búsqueda (buscar por nombre, SKU, QR)
- Filtros: 
  - Categoría (dropdown multi-select)
  - Ubicación (dropdown)
  - Estado (disponible, en préstamo, mantenimiento, dañado, retirado)
  - Tipo (consumible / regular)
- Botón "Exportar CSV"

**Tabla (columnas):**
| Imagen | QR Code | Nombre | SKU | Categoría | Ubicación | Estado | Stock (solo consumibles) | Acciones |
|--------|---------|--------|-----|-----------|-----------|--------|--------------------------|----------|
| Thumbnail 50x50 | MAT-XXX | Laptop HP | LP-001 | Electrónica | Almacén A | Badge verde "Disponible" | - | •••(menú) |
| Thumbnail | MAT-YYY | Tornillos M8 | TOR-008 | Ferretería | Almacén B | Badge azul "En préstamo" | 450/1000 | •••(menú) |

**Badge de Estado (colores):**
- Disponible: Verde
- En Préstamo: Azul
- Mantenimiento: Amarillo
- Dañado: Rojo
- Retirado: Gris

**Menú de Acciones (•••):**
- Ver Detalle
- Editar
- Ver Historial de Préstamos
- Generar Etiqueta QR
- Marcar como Dañado/Mantenimiento
- Eliminar (con confirmación)

#### Modal: Nuevo/Editar Material
**Pestañas:**
1. **Información Básica**
   - Nombre* (text)
   - Descripción (textarea)
   - SKU* (text, único)
   - Código de Barras (text, opcional)
   - Categoría* (select)
   - Ubicación* (select)
   - Imagen del material (upload con preview)

2. **Tipo y Stock**
   - ¿Es consumible? (toggle switch)
   
   **Si es CONSUMIBLE:**
   - Cantidad total* (number)
   - Cantidad disponible* (number, calculado automáticamente)
   - Unidad de medida* (select: unidad, caja, kg, metro, litro)
   - Nivel mínimo de stock* (number, para alertas)
   - Cantidad a reordenar (number, sugerencia cuando esté bajo)
   
   **Si es REGULAR:**
   - Cantidad: 1 (fijo, no editable)

3. **Configuración**
   - ¿Disponible para préstamo? (toggle)
   - ¿Requiere autenticación facial? (toggle, para materiales de alto valor)
   - Estado (select: disponible, mantenimiento, dañado, retirado)
   - Notas adicionales (textarea)

**Código QR:**
- Se genera automáticamente al guardar
- Mostrar vista previa del QR generado
- Botón "Descargar QR" (PNG)

**Botones:**
- Guardar (primario azul)
- Cancelar (secundario gris)

#### Vista Detalle de Material
**Header:**
- Imagen grande del material (200x200)
- Código QR grande
- Nombre del material
- Badge de estado
- SKU
- Botón "Editar" / "Generar Etiqueta QR"

**Tabs:**
1. **Información General**
   - Todos los datos del material en formato lectura
   - Categoría, ubicación, descripción, etc.
   - Si es consumible: gráfico de barras de stock disponible vs total

2. **Historial de Préstamos**
   - Tabla de préstamos pasados y activos
   - Columnas: Empleado, Fecha entrega, Fecha retorno esperada, Fecha retorno real, Estado, Condición
   - Filtros por fecha

3. **Actividad**
   - Timeline de eventos:
     - Creado el...
     - Editado el...
     - Prestado a X el...
     - Devuelto el...
     - Marcado como dañado el...

---

### 4. 📋 CATEGORÍAS Y UBICACIONES

#### Categorías
**Vista:**
- Tabla simple: Nombre | Descripción | ¿Es consumible? | # Materiales | Acciones
- Botón "+ Nueva Categoría"
- Al editar: 
  - Nombre*
  - Descripción
  - ¿Los materiales de esta categoría son consumibles? (toggle)
  - Icono de la categoría (opcional)

#### Ubicaciones
**Vista:**
- Cards de ubicaciones con:
  - Nombre del almacén/ubicación
  - Dirección completa
  - Cantidad de materiales en esa ubicación
  - Estado (activo/inactivo)
- Botón "+ Nueva Ubicación"
- Modal de edición con dirección completa:
  - Nombre*
  - Calle*
  - Número exterior*
  - Número interior
  - Colonia*
  - Código Postal*
  - Ciudad*
  - Estado*
  - País (default: México)

**Restricción de Plan:**
- Plan Freemium: Solo 1 ubicación (mostrar badge "1/1 Ubicaciones")
- Plan Premium: Ilimitadas (mostrar badge "5/∞ Ubicaciones")
- Si intenta crear más en Freemium: modal de upgrade a Premium

---

### 5. 📝 SOLICITUDES DE PRÉSTAMO

**Vista Principal: Tabla de Solicitudes**
**Tabs:**
- Pendientes (destacado con badge naranja del número)
- Aprobadas
- Rechazadas
- Todas

**Tabla (columnas):**
| ID | Empleado | Fecha Solicitud | Fecha Deseada Retiro | Fecha Deseada Retorno | Materiales (# items) | Estado | Acciones |
|----|----------|-----------------|----------------------|-----------------------|----------------------|--------|----------|
| #001 | Juan Pérez | 04/02/2026 | 05/02/2026 | 10/02/2026 | 3 materiales | Badge "Pendiente" | Ver / Aprobar / Rechazar |

**Modal: Ver Detalle de Solicitud**
**Header:**
- ID Solicitud
- Empleado (nombre + foto)
- Estado (badge grande)

**Sección: Información de la Solicitud**
- Fecha de solicitud
- Fecha deseada de retiro
- Fecha deseada de retorno
- Propósito del préstamo (texto)

**Sección: Materiales Solicitados**
- Lista de materiales:
  - Imagen thumbnail
  - Nombre material
  - Categoría
  - Cantidad solicitada (para consumibles)
  - Estado actual del material (disponible/no disponible)
  - Alerta si NO hay stock suficiente (rojo)

**Sección: Revisión (si ya fue revisada)**
- Revisado por: Nombre del inventarista
- Fecha de revisión
- Notas de revisión

**Botones:**
- **Aprobar** (verde) → Abre modal de confirmación
  - Revisar que todos los materiales estén disponibles
  - Confirmar fechas
  - Notas opcionales
  - Botón "Confirmar Aprobación"
  
- **Rechazar** (rojo) → Abre modal
  - Razón del rechazo* (textarea obligatoria)
  - Botón "Confirmar Rechazo"

- **Cancelar** (gris)

---

### 6. 🎯 PRÉSTAMOS ACTIVOS

**Vista Principal: Tabla de Préstamos**
**Tabs:**
- Activos (verde)
- Vencidos (rojo, con número de badge)
- Devueltos (gris)
- Todos

**Filtros:**
- Empleado
- Material
- Rango de fechas
- Estado

**Tabla (columnas):**
| ID | Material | Empleado | Fecha Entrega | Fecha Retorno Esperada | Días Restantes/Vencido | Estado | Acciones |
|----|----------|----------|---------------|------------------------|------------------------|--------|----------|
| #125 | Laptop HP | Juan Pérez | 01/02/2026 | 05/02/2026 | ⚠️ VENCIDO (-1 día) | Badge rojo | Ver / Registrar Devolución |
| #126 | Taladro | María García | 03/02/2026 | 10/02/2026 | 6 días | Badge verde | Ver |

**Modal: Registrar Entrega de Préstamo**
(Se abre cuando se aprueba una solicitud)

**Sección: Escanear QR del Material**
- Botón "Activar Cámara" → Abre escáner QR con cámara web
- O campo manual para ingresar código QR
- Al escanear: muestra info del material escaneado
  - Imagen
  - Nombre
  - Código QR
  - Estado

**Sección: Verificar Identidad del Empleado**
- Foto del empleado
- Nombre completo
- Si el material requiere facial auth:
  - Botón "Activar Verificación Facial" → Abre cámara
  - Estado: "✓ Verificado" o "✗ No verificado"

**Sección: Condición del Material**
- Seleccionar condición actual: (radio buttons)
  - Excelente
  - Bueno
  - Regular
  - Malo
  - Dañado
- Notas sobre condición (textarea, opcional)

**Sección: Firma Digital del Empleado**
- Canvas de firma (área blanca con bordes)
- Botones: Limpiar / Guardar firma
- Preview de la firma capturada

**Sección: Confirmación**
- Resumen:
  - Material: [Nombre]
  - Empleado: [Nombre]
  - Fecha de entrega: [Hoy]
  - Fecha de retorno esperada: [Fecha de la solicitud]
- Botón "Confirmar Entrega" (verde, grande)

**Modal: Registrar Devolución**
(Similar al de entrega)

**Sección: Escanear QR del Material**
- Escáner QR o ingreso manual

**Sección: Condición del Material al Retorno**
- Seleccionar condición: Excelente / Bueno / Regular / Malo / Dañado
- **Si condición es "Dañado":**
  - Textarea obligatoria: "Describe el daño"
  - Toggle: "¿Requiere mantenimiento?"
  - El material se marca automáticamente como "dañado" en inventario

**Sección: Comparación de Condiciones**
- Tabla comparativa:
  | Aspecto | Al Retirar | Al Devolver |
  |---------|------------|-------------|
  | Condición | Bueno | Dañado |
  | Estado | Disponible | Requiere mantenimiento |

**Sección: Firma Digital de Recepción**
- Canvas de firma del inventarista
- Botones: Limpiar / Guardar firma

**Botones:**
- Confirmar Devolución (verde)
- Cancelar

---

### 7. ⏰ EXTENSIONES DE PRÉSTAMO

**Vista: Solicitudes de Extensión**
**Tabs:**
- Pendientes
- Aprobadas
- Rechazadas

**Tabla:**
| ID | Préstamo | Material | Empleado | Fecha Retorno Original | Nueva Fecha Solicitada | Razón | Estado | Acciones |
|----|----------|----------|----------|------------------------|------------------------|-------|--------|----------|
| #15 | #125 | Laptop HP | Juan Pérez | 05/02/2026 | 12/02/2026 | "Proyecto extendido" | Pendiente | Ver / Aprobar / Rechazar |

**Modal: Revisar Extensión**
- Info del préstamo original
- Razón de la extensión (texto del empleado)
- Nueva fecha solicitada
- Historial de extensiones anteriores (si las hay)
- Botones:
  - Aprobar (actualiza fecha de retorno)
  - Rechazar (con razón obligatoria)

---

### 8. 👥 GESTIÓN DE USUARIOS

**Vista: Tabla de Usuarios**
**Tabs:**
- Todos
- Inventaristas
- Empleados
- Bloqueados

**Tabla:**
| Avatar | Nombre | Email | Tipo | Préstamos Activos | Estado | Acciones |
|--------|--------|-------|------|-------------------|--------|----------|
| 👤 | Juan Pérez | juan@empresa.com | Empleado | 2 | ✓ Activo | Ver / Editar / Bloquear |
| 👤 | María García | maria@empresa.com | Inventarista | 0 | ✓ Activo | Ver / Editar |

**Modal: Nuevo Usuario**
- Email*
- Nombre completo*
- Tipo de usuario: (radio) Inventarista / Empleado
- Contraseña temporal*
- Botón "Enviar Invitación" (envía email con link para configurar password)

**Modal: Bloquear Usuario**
- Razón del bloqueo* (textarea)
- Fecha de desbloqueo (date picker, opcional)
- Checkbox: "Bloquear hasta desbloqueo manual"
- Botón "Confirmar Bloqueo"

**Restricción de Plan:**
- Freemium: Máximo 5 usuarios (mostrar "3/5 Usuarios")
- Premium: Ilimitados

---

### 9. 📄 REPORTES Y ESTADÍSTICAS

**Vista: Panel de Reportes**
**Sección: Reportes Predefinidos**
- Card: "Historial Completo de Préstamos"
  - Filtros: Rango de fechas, empleado, material
  - Botón "Generar PDF" / "Exportar Excel"

- Card: "Materiales Más Prestados"
  - Top 10 materiales
  - Gráfica de barras
  - Exportar

- Card: "Empleados con Más Préstamos"
  - Top 10 empleados
  - Tabla con totales
  - Exportar

- Card: "Préstamos Vencidos - Resumen"
  - Lista de todos los vencidos
  - Días de retraso
  - Acciones de seguimiento

- Card: "Inventario Valorizado"
  - Valor total de materiales (si tienen costo de adquisición)
  - Materiales en préstamo vs disponibles
  - Exportar

**Sección: Generador Personalizado**
- Seleccionar tipo de reporte
- Filtros avanzados
- Vista previa
- Generar y descargar

---

### 10. 🏷️ ETIQUETAS QR

**Vista: Generador de Etiquetas**
**Sección: Seleccionar Materiales**
- Tabla de materiales con checkboxes
- Botón "Seleccionar todos"
- Filtros por categoría/ubicación

**Sección: Configurar Plantilla**
- Tamaño de etiqueta: (radio)
  - Pequeña (50x30mm)
  - Mediana (70x50mm)
  - Grande (100x70mm)
- Elementos a incluir: (checkboxes)
  - ✓ Logo de la empresa
  - ✓ Código QR
  - ✓ Nombre del material
  - ✓ Categoría
  - □ Ubicación
  - □ SKU
- Vista previa de la etiqueta

**Botones:**
- Generar PDF (para impresión)
- Guardar como Plantilla

---

### 11. ⚙️ CONFIGURACIÓN DE CUENTA

**Tabs:**

#### 1. Información de la Empresa
- Logo de la empresa (upload con preview circular)
- Nombre de la empresa*
- Dirección completa
- Teléfono
- Email de contacto
- Botón "Guardar Cambios"

#### 2. Plan y Suscripción
- Plan actual: (Card destacada)
  - "Freemium" o "Premium"
  - Beneficios del plan
  - Límites: X/1 Ubicaciones, Y/5 Usuarios
- Si es Freemium:
  - Botón "Actualizar a Premium" (destacado)
  - Comparativa de planes
- Si es Premium:
  - Fecha de renovación
  - Método de pago
  - Historial de pagos

#### 3. Seguridad
- Cambiar contraseña
- Autenticación de dos factores (toggle)
- Sesiones activas (lista de dispositivos)
- Botón "Cerrar todas las sesiones"

#### 4. Notificaciones
- Toggles para configurar:
  - ✓ Nuevas solicitudes de préstamo
  - ✓ Préstamos próximos a vencer (1 día antes)
  - ✓ Préstamos vencidos
  - ✓ Stock bajo en materiales
  - ✓ Nuevas extensiones solicitadas
  - □ Resumen diario por email

---

## ELEMENTOS DE UI COMUNES

### Sidebar Navegación
**Logo** (arriba)
**Menú:**
- 📊 Dashboard
- 📦 Materiales
  - Todos los materiales
  - Categorías
  - Ubicaciones
- 📋 Solicitudes (badge si hay pendientes)
- 🎯 Préstamos
  - Activos
  - Vencidos (badge rojo)
  - Historial
- ⏰ Extensiones (badge si hay pendientes)
- 👥 Usuarios
- 📄 Reportes
- 🏷️ Etiquetas QR

**Footer Sidebar:**
- ⚙️ Configuración
- 👤 Perfil (nombre + avatar)
- 🚪 Cerrar Sesión

### Header Global
- Breadcrumbs (Inicio > Materiales > Detalle)
- Barra de búsqueda global
- Iconos:
  - 🔔 Notificaciones (badge si hay nuevas)
  - 👤 Avatar del usuario (dropdown con opciones)

### Estados de Carga
- Skeleton loaders para tablas
- Spinners para acciones
- Mensajes de confirmación (toast/snackbar)

### Responsive
- Desktop: Sidebar fijo
- Tablet: Sidebar colapsable
- Mobile: Menú hamburguesa

---

## INTERACCIONES Y ANIMACIONES

- Hover en botones: ligero cambio de brillo
- Cards con sombra al hover
- Transiciones suaves (200-300ms)
- Modals con overlay oscuro (backdrop)
- Tooltips en iconos
- Loading states claros
- Toast notifications (esquina superior derecha)
  - Éxito: verde
  - Error: rojo
  - Advertencia: amarillo
  - Info: azul

---

## ICONOGRAFÍA RECOMENDADA

Usar un set consistente como:
- **Heroicons** (recomendado)
- Material Icons
- Feather Icons

**Iconos clave:**
- 📦 Caja para materiales
- 🔍 Lupa para búsqueda
- ➕ Plus para agregar
- ✏️ Lápiz para editar
- 🗑️ Papelera para eliminar
- 📊 Gráficas para dashboard
- 👤 Persona para usuarios
- 🎯 Diana para préstamos
- ⏰ Reloj para extensiones
- 📷 Cámara para escaneo QR
- ✓ Check para confirmaciones
- ⚠️ Triángulo para advertencias
- 🔔 Campana para notificaciones

---

## PRIORIDADES DE IMPLEMENTACIÓN

**Fase 1 (MVP):**
1. Login
2. Dashboard con métricas básicas
3. Gestión de materiales (CRUD completo)
4. Solicitudes de préstamo (ver, aprobar, rechazar)
5. Registro de entrega de préstamos

**Fase 2:**
6. Registro de devoluciones
7. Extensiones de préstamo
8. Gestión de usuarios
9. Categorías y ubicaciones

**Fase 3:**
10. Reportes básicos
11. Etiquetas QR
12. Notificaciones
13. Configuración de cuenta

---

## REFERENCIAS VISUALES

**Estilo recomendado:**
- Limpio y profesional (estilo SaaS moderno)
- Inspiración: Linear, Notion, Stripe Dashboard
- Layout: Sidebar + contenido principal
- Espaciado generoso (no saturar con información)
- Jerarquía visual clara
- Acciones primarias destacadas

**NO hacer:**
- Diseño sobrecargado
- Muchos colores sin significado
- Tablas sin paginación
- Modals que ocupen toda la pantalla
- Formularios sin validación visual

---

## STACK TECNOLÓGICO FRONTEND (Front_End_SaaS/)

### Framework Base
- **Next.js 14+** (App Router)
  - React 18+
  - TypeScript
  - Server Components + Client Components
  - Variables de entorno (.env.local)

### UI y Estilos
- **Tailwind CSS** (utility-first CSS)
- **Shadcn/ui** (componentes base reutilizables)
  - Buttons, Modals, Dropdowns, etc.
- **Lucide Icons** o **Heroicons** (iconografía consistente)

### Gestión de Estado
- **Zustand** (estado global ligero)
- **TanStack Query (React Query)** (cache y sincronización de datos con backend)

### Formularios y Validación
- **React Hook Form** (manejo de formularios)
- **Zod** (validación de schemas)

### Tablas
- **TanStack Table** (tablas potentes con filtros, paginación, sorting)

### Gráficas
- **Recharts** o **Chart.js** (visualización de datos)

### Escaneo QR
- **@zxing/browser** o **react-qr-scanner** (escaneo desde cámara web)

### Firma Digital
- **react-signature-canvas** (captura de firma)

### Comunicación con Backend
- **Axios** (HTTP client)
- **TanStack Query** (para queries y mutations)
- Variables de entorno para API URL

### Autenticación
- **JWT** almacenado en localStorage/sessionStorage
- Middleware de Next.js para proteger rutas
- Refresh token automático

### Notificaciones
- **react-hot-toast** o **sonner** (toast notifications)

### Date Handling
- **date-fns** (manipulación de fechas)

---

## ESTRUCTURA DE CARPETAS RECOMENDADA

### Backend (Pack-a-Stock/)
```
Pack-a-Stock/
├── .env                          # Variables de entorno (IGNORAR EN GIT)
├── .env.example                  # Plantilla de variables
├── docker-compose.yml            # Orquestación de contenedores
├── Dockerfile                    # Imagen del backend
├── entrypoint.sh                 # Script de inicio
├── requirements.txt              # Dependencias Python
├── manage.py
├── pack_a_stock_api/
│   ├── settings.py              # ⚠️ Usar variables de entorno
│   ├── urls.py
│   └── wsgi.py
├── accounts/
├── materials/
├── loans/
├── audit/
├── labels/
└── media/                        # Archivos subidos (QR, imágenes)
    └── qr_codes/
```

### Frontend (Front_End_SaaS/)
```
Front_End_SaaS/
├── .env.local                    # Variables de entorno (IGNORAR EN GIT)
├── .env.example                  # Plantilla de variables
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── recuperar-password/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx            # Sidebar + Header global
│   │   ├── page.tsx              # Dashboard principal
│   │   ├── materiales/
│   │   │   ├── page.tsx
│   │   │   ├── nuevo/
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   ├── categorias/
│   │   │   └── ubicaciones/
│   │   ├── solicitudes/
│   │   │   └── page.tsx
│   │   ├── prestamos/
│   │   │   ├── page.tsx
│   │   │   ├── activos/
│   │   │   └── vencidos/
│   │   ├── extensiones/
│   │   ├── usuarios/
│   │   ├── reportes/
│   │   ├── etiquetas/
│   │   └── configuracion/
│   └── api/                      # Route handlers si es necesario
├── components/
│   ├── ui/                       # Shadcn components
│   │   ├── button.tsx
│   │   ├── modal.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Breadcrumbs.tsx
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── AlertCard.tsx
│   │   └── ActivityTimeline.tsx
│   ├── materiales/
│   │   ├── MaterialTable.tsx
│   │   ├── MaterialForm.tsx
│   │   ├── MaterialDetail.tsx
│   │   └── QRScanner.tsx
│   ├── prestamos/
│   │   ├── LoanTable.tsx
│   │   ├── EntregaModal.tsx
│   │   ├── DevolucionModal.tsx
│   │   └── SignatureCanvas.tsx
│   └── common/
│       ├── DataTable.tsx
│       ├── StatusBadge.tsx
│       ├── Modal.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   ├── api.ts                    # Axios instance + config con env vars
│   ├── auth.ts                   # Autenticación helpers
│   ├── utils.ts                  # Utilidades generales
│   └── constants.ts              # Constantes (usar env vars donde aplique)
├── hooks/
│   ├── useAuth.ts
│   ├── useMaterials.ts
│   ├── useLoans.ts
│   └── useQRScanner.ts
├── store/
│   └── authStore.ts              # Zustand store
├── types/
│   ├── material.ts
│   ├── loan.ts
│   ├── user.ts
│   └── api.ts
└── public/
    ├── images/
    └── icons/
```


---

## SIGUIENTE PASO: INICIAR DESARROLLO

### ✅ Checklist de Preparación

**Backend (Pack-a-Stock/):**
- [x] Modelos de base de datos completos
- [x] API REST funcionando
- [x] Autenticación JWT implementada
- [x] Documentación de endpoints
- [ ] Actualizar docker-compose.yml con variables de entorno
- [ ] Crear .env.example con todas las variables necesarias
- [ ] Crear entrypoint.sh para Docker
- [ ] Actualizar Dockerfile con mejores prácticas
- [ ] Configurar CORS para frontend
- [ ] Agregar endpoints específicos para app móvil

**Frontend (Front_End_SaaS/):**
- [ ] Inicializar proyecto Next.js 14 con TypeScript
- [ ] Configurar Tailwind CSS + Shadcn/ui
- [ ] Instalar dependencias (React Query, Zustand, Axios, etc.)
- [ ] Crear estructura de carpetas
- [ ] Configurar .env.local con NEXT_PUBLIC_API_URL
- [ ] Crear .env.example
- [ ] Configurar axios instance con interceptors JWT
- [ ] Implementar middleware de autenticación
- [ ] Crear layout base (Sidebar + Header)

**Docker & Deployment:**
- [ ] Verificar docker-compose funciona con .env
- [ ] Crear docker-compose.prod.yml para producción
- [ ] Configurar Nginx como reverse proxy (opcional)
- [ ] Documentar proceso de deployment
- [ ] Crear scripts de backup para PostgreSQL
- [ ] Configurar certificados SSL (Let's Encrypt)

**Móvil (Futuro):**
- [ ] Definir stack (React Native vs Flutter)
- [ ] Diseñar mockups de interfaz móvil
- [ ] Listar endpoints API necesarios adicionales
- [ ] Configurar Firebase Cloud Messaging para push notifications

---

## 🚀 COMANDOS PARA INICIAR

### Backend (Pack-a-Stock/)

```bash
# Desarrollo local (sin Docker)
cd Pack-a-Stock
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear .env desde ejemplo
cp .env.example .env
# Editar .env con tus valores

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py create_superadmin

# Correr servidor
python manage.py runserver
# API disponible en: http://localhost:8000/api/

# ---

# Desarrollo con Docker
cd Pack-a-Stock
cp .env.example .env
# Editar .env

docker-compose up --build
# API disponible en: http://localhost:8000/api/
# PgAdmin en: http://localhost:5050 (si lo agregas)

# Ver logs
docker-compose logs -f backend

# Ejecutar comandos dentro del contenedor
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Frontend (Front_End_SaaS/)

```bash
# Crear proyecto Next.js
cd Front_End_SaaS
npx create-next-app@latest . --typescript --tailwind --app --src-dir

# Instalar Shadcn/ui
npx shadcn-ui@latest init

# Instalar dependencias adicionales
npm install zustand @tanstack/react-query @tanstack/react-query-devtools
npm install axios zod react-hook-form @hookform/resolvers
npm install date-fns lucide-react recharts react-hot-toast
npm install @zxing/browser react-signature-canvas
npm install @tanstack/react-table

# Instalar tipos
npm install -D @types/node @types/react @types/react-dom

# Crear .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Copiar ejemplo
cp .env.local .env.example

# Ejecutar en desarrollo
npm run dev
# Aplicación en: http://localhost:3000

# Build para producción
npm run build
npm start
```

### Producción (Todo junto con Docker)

```bash
# En el servidor VPS

# 1. Backend
cd Pack-a-Stock
cp .env.example .env
nano .env  # Configurar para producción

docker-compose -f docker-compose.prod.yml up -d --build

# 2. Frontend (si usas Docker también)
cd ../Front_End_SaaS
cp .env.example .env.production
nano .env.production  # NEXT_PUBLIC_API_URL=https://api.tudominio.com

docker build -t packastock-frontend .
docker run -d -p 3000:3000 --env-file .env.production packastock-frontend

# O desplegar en Vercel
vercel --prod
```

---

## 📋 TAREAS INMEDIATAS (SPRINT 1)

### Semana 1: Setup y Configuración

**Backend:**
1. Crear `.env.example` con todas las variables documentadas
2. Actualizar `docker-compose.yml` para usar variables .env
3. Crear `entrypoint.sh` para esperar PostgreSQL
4. Actualizar `Dockerfile` con mejores prácticas
5. Configurar CORS correctamente en `settings.py`
6. Documentar endpoints en Swagger/OpenAPI
7. Crear endpoint `GET /api/health/` para health checks

**Frontend:**
8. Inicializar proyecto Next.js en `Front_End_SaaS/`
9. Configurar Tailwind + Shadcn/ui
10. Crear estructura de carpetas completa
11. Configurar `.env.local` y `.env.example`
12. Crear `lib/api.ts` con axios y interceptors JWT
13. Crear layout base (Sidebar + Header vacío)
14. Implementar página de login funcional

**Docker:**
15. Verificar que todo funcione con `docker-compose up`
16. Documentar comandos en `README.md`

### Semana 2: Autenticación y Dashboard

**Backend:**
17. Verificar endpoints de autenticación funcionan correctamente
18. Agregar rate limiting a login
19. Implementar refresh token automático

**Frontend:**
20. Implementar autenticación completa (login, logout, refresh)
21. Crear middleware para rutas protegidas
22. Crear store de Zustand para auth
23. Implementar Dashboard con métricas (consumiendo API)
24. Crear componente MetricCard reutilizable
25. Implementar navegación sidebar funcional

### Semana 3: Gestión de Materiales (MVP)

**Backend:**
26. Verificar endpoints de materiales
27. Optimizar queries (select_related, prefetch_related)
28. Agregar paginación a lista de materiales

**Frontend:**
29. Crear tabla de materiales con TanStack Table
30. Implementar búsqueda y filtros
31. Crear modal de nuevo/editar material
32. Implementar subida de imágenes
33. Mostrar QR codes generados
34. Crear página de detalle de material

### Semana 4: Solicitudes y Préstamos (MVP)

**Backend:**
35. Verificar endpoints de solicitudes
36. Agregar notificaciones por email
37. Optimizar queries de préstamos

**Frontend:**
38. Crear tabla de solicitudes pendientes
39. Modal de detalle de solicitud
40. Aprobar/rechazar solicitudes
41. Tabla de préstamos activos
42. Implementar escaneo QR con cámara web
43. Modal de entrega de préstamo con firma digital

---

## 🎯 DEFINICIÓN DE "HECHO" (Definition of Done)

Para cada funcionalidad:

- [ ] Código funciona correctamente
- [ ] Variables de entorno usadas (no valores hardcodeados)
- [ ] Responsive (desktop, tablet, móvil)
- [ ] Manejo de errores implementado
- [ ] Loading states visibles
- [ ] Mensajes de éxito/error al usuario
- [ ] No hay console.errors en navegador
- [ ] Funciona con datos reales de la API
- [ ] Funciona en Docker
- [ ] Documentado en README si es necesario

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### Variables de Entorno
- ❌ NUNCA subir `.env` a Git
- ✅ SIEMPRE usar `.env.example` como plantilla
- ✅ Documentar cada variable en README
- ✅ Usar `python-decouple` o `os.getenv()` en Django
- ✅ Usar `process.env` en Next.js (prefijo NEXT_PUBLIC_ para cliente)

### Docker
- Usar volúmenes para persistencia de datos
- Esperar a que PostgreSQL esté listo antes de migrar
- Usar multi-stage builds en producción
- No exponer puertos innecesarios
- Usar networks para comunicación entre contenedores

### Seguridad
- JWT en localStorage (frontend) con httpOnly cookies (mejor opción)
- Refresh token automático antes de expirar
- Rate limiting en endpoints críticos
- CORS restrictivo en producción
- HTTPS obligatorio en producción
- Variables secretas nunca en el código

### Móvil
- Misma API para web y móvil
- Versionado de API (v1, v2) para compatibilidad
- Push notifications con FCM
- Autenticación biométrica opcional
- Modo offline con sincronización posterior

---

## 📞 PRÓXIMOS PASOS - ¿QUÉ HACEMOS AHORA?

**Opción A: Setup Backend** (RECOMENDADO PRIMERO)
- Actualizar archivos de configuración Docker
- Crear .env.example
- Verificar que todo funcione con docker-compose

**Opción B: Setup Frontend**
- Inicializar proyecto Next.js
- Configurar dependencias
- Crear estructura base

**Opción C: Ambos en paralelo**
- Yo trabajo en backend
- Tú o alguien más en frontend

¿Por cuál opción quieres empezar?
