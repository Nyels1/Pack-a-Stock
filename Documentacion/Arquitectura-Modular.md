# Pack-a-Stock - Arquitectura Modular

## Estructura del Proyecto

```
PACK-A-STOCK-FRONT-BACK/
├── Front_End_SaaS/          # Frontend React Web
│   ├── src/
│   │   ├── modules/         # Módulos del frontend
│   │   ├── components/      # Componentes compartidos
│   │   ├── services/        # API calls
│   │   └── utils/           # Utilidades
│   └── package.json
│
└── Pack-a-Stock/            # Backend Django REST Framework
    ├── pack_a_stock_api/    # Proyecto Django principal
    ├── accounts/            # App: Cuentas y autenticación
    ├── materials/           # App: Inventario y materiales
    ├── loans/               # App: Préstamos
    ├── notifications/       # App: Notificaciones
    └── requirements.txt
```

---

## Módulos del Sistema (Orden de Implementación)

### FASE 1: Autenticación y Cuentas (CORE)
Prioridad: CRÍTICA

#### Backend (Django App: `accounts`)
- **Modelos:**
  - `Account` (Empresa/Cuenta)
  - `User` (Inventarista/Empleado)
  
- **Funcionalidades:**
  - ✅ Registro de cuenta (inventarista crea empresa)
  - ✅ Login/Logout con JWT
  - ✅ Gestión de perfil
  - ✅ CRUD de empleados
  - ✅ Validación de límites por plan (freemium/premium)

- **Endpoints:**
  ```
  POST   /api/auth/register              # Crear cuenta + inventarista
  POST   /api/auth/login                 # Login JWT
  POST   /api/auth/logout                # Logout
  POST   /api/auth/register-employee     # Crear empleado
  GET    /api/users/me                   # Perfil actual
  PUT    /api/users/me                   # Actualizar perfil
  GET    /api/users/                     # Listar empleados
  PUT    /api/users/:id/block            # Bloquear usuario
  ```

#### Frontend (React Module: `Auth`)
- **Páginas:**
  - `Register.tsx` - Registro de cuenta
  - `Login.tsx` - Inicio de sesión
  - `Profile.tsx` - Perfil de usuario
  - `EmployeeManagement.tsx` - Gestión de empleados

- **Componentes:**
  - `PrivateRoute` - Protección de rutas
  - `AuthProvider` - Contexto de autenticación

Dependencias Backend:
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
- psycopg2-binary
- boto3
- django-storages

Dependencias Frontend:
- axios
- react-router-dom
- @tanstack/react-query
- zustand (state management)

---

### FASE 2: Gestión de Inventario
Prioridad: ALTA

#### Backend (Django App: `materials`)
- **Modelos:**
  - `Category` (Categorías)
  - `Location` (Almacenes/Ubicaciones)
  - `Material` (Materiales/Equipos)

- **Funcionalidades:**
  - ✅ CRUD de categorías
  - ✅ CRUD de ubicaciones/almacenes (validar límite por plan)
  - ✅ CRUD de materiales
  - ✅ Búsqueda y filtros de materiales
  - ✅ Estados de materiales (disponible, prestado, mantenimiento, etc.)

- **Endpoints:**
  ```
  # Categorías
  GET    /api/categories/               # Listar
  POST   /api/categories/               # Crear
  PUT    /api/categories/:id            # Actualizar
  DELETE /api/categories/:id            # Eliminar
  
  # Ubicaciones
  GET    /api/locations/                # Listar
  POST   /api/locations/                # Crear (validar límite)
  PUT    /api/locations/:id             # Actualizar
  DELETE /api/locations/:id             # Eliminar
  
  # Materiales
  GET    /api/materials/                # Listar con filtros
  POST   /api/materials/                # Crear
  GET    /api/materials/:id             # Detalle
  PUT    /api/materials/:id             # Actualizar
  DELETE /api/materials/:id             # Eliminar
  PUT    /api/materials/:id/status      # Cambiar estado
  ```

#### Frontend (React Module: `Inventory`)
- **Páginas:**
  - `MaterialsList.tsx` - Listado de materiales
  - `MaterialForm.tsx` - Crear/Editar material
  - `CategoriesManager.tsx` - Gestión de categorías
  - `LocationsManager.tsx` - Gestión de almacenes

- **Componentes:**
  - `MaterialCard` - Tarjeta de material
  - `MaterialFilters` - Filtros de búsqueda
  - `StatusBadge` - Badge de estado

Dependencias Backend:
- pillow
- django-filter
- boto3
- django-storages

Dependencias Frontend:
- react-table
- react-hook-form
- zod (validación)

---

### FASE 3: Sistema de Etiquetas QR
Prioridad: ALTA

#### Backend (Django App: `materials` - extensión)
- **Modelos:**
  - `LabelTemplate` (Plantillas de etiquetas)
  - `CompanyLogo` (Logo de empresa para etiquetas)

- **Funcionalidades:**
  - ✅ Generación de código QR por material (ID del material)
  - ✅ Plantillas de etiquetas personalizables
  - ✅ Subida de logo de empresa
  - ✅ Generación de etiquetas en PDF/PNG
  - ✅ Generación batch (múltiples etiquetas)

- **Endpoints:**
  ```
  # QR y Etiquetas
  POST   /api/materials/:id/generate-qr        # Generar QR individual
  POST   /api/labels/generate                  # Generar etiqueta
  POST   /api/labels/generate-batch            # Generar múltiples
  
  # Plantillas
  GET    /api/labels/templates/                # Listar plantillas
  POST   /api/labels/templates/                # Crear plantilla
  
  # Logo
  POST   /api/config/logo                      # Subir logo
  GET    /api/config/logo                      # Obtener logo
  ```

#### Frontend (React Module: `Labels`)
- **Páginas:**
  - `QRGenerator.tsx` - Generador de QR
  - `LabelDesigner.tsx` - Diseñador de etiquetas
  - `BatchGenerator.tsx` - Generación masiva

- **Componentes:**
  - `QRPreview` - Vista previa de QR
  - `LabelPreview` - Vista previa de etiqueta
  - `LogoUploader` - Subida de logo

Dependencias Backend:
- qrcode
- reportlab
- boto3
- django-storages

Dependencias Frontend:
- react-qr-code
- jspdf (preview PDF)

---

### FASE 4: Sistema de Préstamos
Prioridad: ALTA

#### Backend (Django App: `loans`)
- **Modelos:**
  - `LoanRequest` (Solicitudes)
  - `LoanRequestItem` (Ítems de solicitud)
  - `Loan` (Préstamos activos)
  - `LoanExtension` (Extensiones)

- **Funcionalidades:**
  - ✅ Crear solicitud de préstamo
  - ✅ Aprobar/rechazar solicitudes
  - ✅ Crear préstamo desde solicitud
  - ✅ Registrar devolución
  - ✅ Solicitar extensión
  - ✅ Aprobar/rechazar extensión
  - ✅ Detección automática de retrasos
  - ✅ Bloqueo automático por retrasos

- **Endpoints:**
  ```
  # Solicitudes
  GET    /api/loan-requests/                    # Listar
  POST   /api/loan-requests/                    # Crear
  GET    /api/loan-requests/:id                 # Detalle
  PUT    /api/loan-requests/:id/approve         # Aprobar
  PUT    /api/loan-requests/:id/reject          # Rechazar
  DELETE /api/loan-requests/:id                 # Cancelar
  
  # Préstamos
  GET    /api/loans/                            # Listar
  POST   /api/loans/from-request/:id            # Crear desde solicitud
  GET    /api/loans/:id                         # Detalle
  PUT    /api/loans/:id/return                  # Registrar devolución
  
  # Extensiones
  POST   /api/loans/:id/extend                  # Solicitar extensión
  GET    /api/loans/:id/extensions              # Listar extensiones
  PUT    /api/loans/extensions/:id/approve      # Aprobar
  PUT    /api/loans/extensions/:id/reject       # Rechazar
  ```

#### Frontend (React Module: `Loans`)
- **Páginas Inventarista:**
  - `LoanRequestsList.tsx` - Solicitudes pendientes
  - `LoanRequestDetail.tsx` - Detalle de solicitud
  - `ActiveLoansList.tsx` - Préstamos activos
  - `LoanDetail.tsx` - Detalle de préstamo

- **Páginas Empleado:**
  - `RequestLoan.tsx` - Solicitar préstamo
  - `MyLoans.tsx` - Mis préstamos
  - `MyRequests.tsx` - Mis solicitudes

- **Componentes:**
  - `LoanCard` - Tarjeta de préstamo
  - `ApprovalModal` - Modal de aprobación
  - `ReturnModal` - Modal de devolución
  - `ExtensionForm` - Formulario de extensión

Dependencias Backend:
- celery
- redis
- django-celery-beat

Dependencias Frontend:
- react-calendar
- date-fns

---

### FASE 5: Notificaciones
Prioridad: MEDIA

#### Backend (Django App: `notifications`)
- **Modelos:**
  - `Notification` (Notificaciones)

- **Funcionalidades:**
  - ✅ Crear notificaciones automáticas
  - ✅ Marcar como leída
  - ✅ Recordatorios de devolución
  - ✅ Alertas de retraso
  - ✅ Notificación de aprobación/rechazo

- **Endpoints:**
  ```
  GET    /api/notifications/                    # Listar
  PUT    /api/notifications/:id/read            # Marcar como leída
  PUT    /api/notifications/read-all            # Marcar todas
  GET    /api/notifications/unread-count        # Contador
  ```

#### Frontend (React Module: `Notifications`)
- **Componentes:**
  - `NotificationBell` - Campana de notificaciones
  - `NotificationDropdown` - Dropdown de notificaciones
  - `NotificationItem` - Item individual

Dependencias Backend:
- django-channels (WebSockets - opcional)

Dependencias Frontend:
- react-toastify

---

### FASE 6: Reportes y Dashboard
Prioridad: MEDIA

#### Backend (Django App: `reports`)
- **Funcionalidades:**
  - ✅ Dashboard con estadísticas
  - ✅ Reporte de préstamos
  - ✅ Reporte de uso de materiales
  - ✅ Reporte de actividad de usuarios
  - ✅ Top materiales más prestados
  - ✅ Top usuarios más activos

- **Endpoints:**
  ```
  GET    /api/reports/dashboard                 # Dashboard
  GET    /api/reports/loans                     # Reporte préstamos
  GET    /api/reports/materials-usage           # Uso materiales
  GET    /api/reports/user-activity             # Actividad usuarios
  ```

#### Frontend (React Module: `Reports`)
- **Páginas:**
  - `Dashboard.tsx` - Dashboard principal
  - `LoansReport.tsx` - Reporte de préstamos
  - `MaterialsReport.tsx` - Reporte de materiales
  - `UsersReport.tsx` - Reporte de usuarios

- **Componentes:**
  - `StatCard` - Tarjeta de estadística
  - `Chart` - Gráficas
  - `ReportFilters` - Filtros de reportes

Dependencias Frontend:
- recharts
- react-export-table-to-excel

---

### FASE 7: Suscripciones (Freemium/Premium)
Prioridad: MEDIA-BAJA

#### Backend (Django App: `subscriptions`)
- **Modelos:**
  - Campos en `Account` para suscripción

- **Funcionalidades:**
  - ✅ Ver planes disponibles
  - ✅ Upgrade a premium
  - ✅ Cancelar suscripción
  - ✅ Validación de límites en todas las operaciones

- **Endpoints:**
  ```
  GET    /api/subscription/plans                # Ver planes
  POST   /api/subscription/upgrade              # Actualizar
  POST   /api/subscription/cancel               # Cancelar
  GET    /api/subscription/current              # Plan actual
  ```

#### Frontend (React Module: `Subscription`)
- **Páginas:**
  - `Plans.tsx` - Planes disponibles
  - `BillingSettings.tsx` - Configuración de facturación

Dependencias Backend:
- stripe (pagos - opcional por ahora)

---

### FASE 8: Configuración y Auditoría
Prioridad: BAJA

#### Backend (Django App: `config`)
- **Modelos:**
  - `AuditLog` (Registro de auditoría)
  - `SystemConfig` (Configuración del sistema)

- **Funcionalidades:**
  - ✅ Configuración de cuenta
  - ✅ Registro de auditoría
  - ✅ Logs de actividad

- **Endpoints:**
  ```
  GET    /api/config/account                    # Config cuenta
  PUT    /api/config/account                    # Actualizar config
  GET    /api/audit-logs/                       # Logs de auditoría
  ```

#### Frontend (React Module: `Settings`)
- **Páginas:**
  - `AccountSettings.tsx` - Configuración de cuenta
  - `AuditLogs.tsx` - Logs de auditoría

---

### FASE 9: Facial Recognition (FUTURO)
Prioridad: PENDIENTE

#### Backend (Django App: `accounts` - extensión)
- Funcionalidades:
  - Registro de foto del inventarista
  - Autenticación facial con Deepface
  - Login alternativo con facial

Dependencias Backend (FUTURO):
- deepface
- tensorflow
- opencv-python

---

## Priorización de Desarrollo

### Sprint 1 (2-3 semanas): MVP Básico
1. FASE 1: Autenticación y Cuentas
2. FASE 2: Gestión de Inventario (sin QR)

### Sprint 2 (2 semanas): Funcionalidad Core
3. FASE 3: Sistema de Etiquetas QR
4. FASE 4: Sistema de Préstamos (básico)

### Sprint 3 (2 semanas): Funcionalidad Completa
5. FASE 4: Préstamos (extensiones y validaciones)
6. FASE 5: Eventos en Tiempo Real (Celery + WebSockets)

### Sprint 4 (1-2 semanas): Analytics
7. FASE 6: Reportes y Dashboard

### Sprint 5 (1 semana): Monetización
8. FASE 7: Suscripciones

### Sprint 6 (1 semana): Extras
9. FASE 8: Configuración y Auditoría

### Backlog: Futuro
10. FASE 9: Facial Recognition

---

## Dependencias entre Módulos

```
FASE 1 (Auth) 
    ↓
FASE 2 (Inventario) → FASE 3 (QR/Etiquetas)
    ↓
FASE 4 (Préstamos) → FASE 5 (Notificaciones)
    ↓
FASE 6 (Reportes)
    ↓
FASE 7 (Suscripciones)
    ↓
FASE 8 (Config/Auditoría)
```

---

## Setup Inicial de Cada Carpeta

### Backend (Pack-a-Stock/)
```bash
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar Django
pip install django djangorestframework djangorestframework-simplejwt

# Crear proyecto
django-admin startproject pack_a_stock_api .

# Crear apps por fase
python manage.py startapp accounts
python manage.py startapp materials
python manage.py startapp loans
python manage.py startapp reports
```

### Frontend (Front_End_SaaS/)
```bash
# Crear proyecto React con Vite
npm create vite@latest . -- --template react-ts

# Instalar dependencias base
npm install react-router-dom axios @tanstack/react-query zustand

# Estructura de carpetas
mkdir -p src/modules/{auth,inventory,labels,loans,notifications,reports,settings}
mkdir -p src/components/common
mkdir -p src/services
mkdir -p src/utils
```

---

## Notas Importantes

1. Desarrollo Modular: Cada fase es independiente pero sigue el orden de dependencias
2. Testing: Cada módulo debe tener sus propias pruebas antes de pasar al siguiente
3. Documentación: Actualizar documentación al completar cada fase
4. Git: Branch por módulo/fase (ej: `feature/auth-module`, `feature/inventory-module`)
5. Base de Datos: Migraciones incrementales por cada app/fase
6. Almacenamiento: Usar buckets S3 para todos los archivos media (logos, imágenes, QR, PDFs)
7. PWA: Configurar service workers y manifest desde el inicio
8. Variables de Entorno: Usar .env para todas las configuraciones sensibles
9. Docker: Desarrollo y producción con Docker Compose
10. Seguridad: SSL/TLS, CORS, CSRF configurados correctamente
