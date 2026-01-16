# Pack-a-Stock - Sistema de Gestión de Préstamos de Materiales

## 📋 Descripción General

**Pack-a-Stock** es un sistema SaaS multi-tenant dual (Web + Mobile) para la gestión de préstamos de materiales y equipos empresariales. Permite a las organizaciones gestionar sus recursos mediante códigos QR individuales. Los inventaristas controlan los préstamos desde la plataforma web, mientras que los empleados pueden solicitar materiales desde sus dispositivos móviles.

### Características Principales
- � **SaaS Multi-Tenant**: Múltiples organizaciones/empresas en una sola plataforma
- 📱 **Plataforma Dual**: Web (inventaristas) + Mobile (empleados)
- 🔐 **Autenticación Biométrica**: Reconocimiento facial para artículos de alto valor
- 📦 **Trazabilidad Completa**: Seguimiento detallado de cada préstamo
- 🏷️ **Etiquetas QR Personalizadas**: Impresión con logo de la empresa
- ⏰ **Control de Retrasos**: Bloqueo automático por devoluciones tardías
- 📊 **Reportes**: Dashboards y estadísticas de uso por organización

---

## 🏗️ Arquitectura del Sistema

### Plataformas
1. **Web Application** (Inventaristas)
   - Gestión de materiales y categorías
   - Aprobación/rechazo de solicitudes
   - Entrega y devolución de préstamos
   - Generación de etiquetas QR
   - Reportes y estadísticas

2. **Mobile Application** (Usuarios)
   - Solicitud de préstamos
   - Escaneo de códigos QR
   - Autenticación facial (artículos caros)
   - Historial de préstamos
   - Notificaciones

### Stack Tecnológico

**Backend**
- Python 3.11+
- Django 4.2+ REST Framework
- PostgreSQL 15+
- Redis (cache y Celery broker)
- Gunicorn (WSGI server)
- Nginx (reverse proxy)

**Frontend**
- React 18+ con TypeScript
- Vite (build tool)
- PWA (Progressive Web App)
- Service Workers para offline support

**Almacenamiento**
- AWS S3 / Google Cloud Storage / MinIO
- django-storages para integración
- Bucket separado para: logos, imágenes de materiales, etiquetas QR generadas

**Autenticación**
- JWT (djangorestframework-simplejwt)
- Deepface para facial recognition (pendiente)

**Infraestructura**
- Docker + Docker Compose
- CI/CD con GitHub Actions
- Variables de entorno (.env)
- SSL/TLS (Let's Encrypt)

**Monitoreo**
- Logs centralizados
- Sentry para error tracking
- PostgreSQL backups automáticos

---

## 🗄️ Modelos de Base de Datos (PostgreSQL)

### 1. Accounts (Cuentas/Empresas)
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_plan VARCHAR(50) NOT NULL DEFAULT 'freemium', -- 'freemium', 'premium'
    max_locations INTEGER DEFAULT 1, -- Freemium: 1, Premium: ilimitado o más
    is_active BOOLEAN DEFAULT TRUE,
    subscription_start_date DATE,
    subscription_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_is_active ON accounts(is_active);
CREATE INDEX idx_accounts_subscription_plan ON accounts(subscription_plan);
```

### 2. Users (Usuarios)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'inventarista' (owner/admin), 'employee'
    face_encoding TEXT, -- Para reconocimiento facial
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_reason TEXT,
    blocked_until TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_account ON users(account_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_is_blocked ON users(is_blocked);
```

### 3. Categories (Categorías)
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    requires_facial_auth BOOLEAN DEFAULT FALSE, -- Para artículos de alto valor
    max_loan_days INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_account ON categories(account_id);
CREATE INDEX idx_categories_is_active ON categories(is_active);
```

### 4. Locations (Ubicaciones/Almacenes)
```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    building VARCHAR(255),
    floor VARCHAR(50),
    room VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_account ON locations(account_id);
CREATE INDEX idx_locations_is_active ON locations(is_active);

-- Nota: El plan Freemium permite 1 almacén, Premium permite múltiples
```

### 5. Materials (Materiales)
```sql
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    location_id INTEGER REFERENCES locations(id),
    qr_code VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    acquisition_date DATE,
    acquisition_cost DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'available', -- 'available', 'on_loan', 'maintenance', 'damaged', 'retired'
    condition VARCHAR(50) DEFAULT 'good', -- 'good', 'fair', 'poor'
    notes TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materials_account ON materials(account_id);
CREATE INDEX idx_materials_category ON materials(category_id);
CREATE INDEX idx_materials_location ON materials(location_id);
CREATE INDEX idx_materials_qr_code ON materials(qr_code);
CREATE INDEX idx_materials_status ON materials(status);
CREATE INDEX idx_materials_is_active ON materials(is_active);
```

### 6. Loan Requests (Solicitudes de Préstamo)
```sql
CREATE TABLE loan_requests (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    desired_pickup_date DATE NOT NULL,
    desired_return_date DATE NOT NULL,
    purpose TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_requests_account ON loan_requests(account_id);
CREATE INDEX idx_loan_requests_user ON loan_requests(user_id);
CREATE INDEX idx_loan_requests_status ON loan_requests(status);
CREATE INDEX idx_loan_requests_pickup_date ON loan_requests(desired_pickup_date);
```

### 7. Loan Request Items (Artículos de la Solicitud)
```sql
CREATE TABLE loan_request_items (
    id SERIAL PRIMARY KEY,
    loan_request_id INTEGER NOT NULL REFERENCES loan_requests(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materials(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_request_items_request ON loan_request_items(loan_request_id);
CREATE INDEX idx_loan_request_items_material ON loan_request_items(material_id);
```

### 8. Loans (Préstamos Activos)
```sql
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    loan_request_id INTEGER REFERENCES loan_requests(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    material_id INTEGER NOT NULL REFERENCES materials(id),
    issued_by INTEGER NOT NULL REFERENCES users(id),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_return_date DATE NOT NULL,
    actual_return_date TIMESTAMP,
    returned_to INTEGER REFERENCES users(id),
    facial_auth_verified BOOLEAN DEFAULT FALSE,
    facial_auth_at TIMESTAMP,
    pickup_signature TEXT,
    return_signature TEXT,
    condition_on_pickup VARCHAR(50), -- 'good', 'fair', 'poor'
    condition_on_return VARCHAR(50),
    damage_notes TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'returned', 'overdue', 'lost'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loans_account ON loans(account_id);
CREATE INDEX idx_loans_user ON loans(user_id);
CREATE INDEX idx_loans_material ON loans(material_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_expected_return ON loans(expected_return_date);
CREATE INDEX idx_loans_request ON loans(loan_request_id);
```

### 9. Loan Extensions (Extensiones de Préstamo)
```sql
CREATE TABLE loan_extensions (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id),
    requested_by INTEGER NOT NULL REFERENCES users(id),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    new_return_date DATE NOT NULL,
    reason TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_extensions_loan ON loan_extensions(loan_id);
CREATE INDEX idx_loan_extensions_status ON loan_extensions(status);
```

### 10. Notifications (Notificaciones)
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- 'loan_approved', 'loan_rejected', 'return_reminder', 'overdue', 'blocked'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_loan_id INTEGER REFERENCES loans(id),
    related_request_id INTEGER REFERENCES loan_requests(id),
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE INDEX idx_notifications_account ON notifications(account_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_type ON notifications(type);
```

### 11. Audit Logs (Registro de Auditoría)
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'material', 'loan', 'user', 'category', etc.
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_account ON audit_logs(account_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 12. Label Templates (Plantillas de Etiquetas)
```sql
CREATE TABLE label_templates (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- 'small', 'medium', 'large'
    width_mm DECIMAL(5, 2),
    height_mm DECIMAL(5, 2),
    include_logo BOOLEAN DEFAULT TRUE,
    include_qr BOOLEAN DEFAULT TRUE,
    include_name BOOLEAN DEFAULT TRUE,
    include_category BOOLEAN DEFAULT TRUE,
    include_location BOOLEAN DEFAULT FALSE,
    custom_fields JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_label_templates_account ON label_templates(account_id);
CREATE INDEX idx_label_templates_is_default ON label_templates(is_default);
```

---

## 🔌 API Endpoints

### Base URL
```
https://api.pack-a-stock.com/v1
```

---

## 🔐 Autenticación

### POST /auth/register
Registro de nueva cuenta (inventarista crea su empresa)
```json
Request:
{
  "email": "admin@empresa.com",
  "password": "securePassword123",
  "full_name": "Juan Pérez",
  "company_name": "Empresa Tech Solutions S.A.",
  "subscription_plan": "freemium"
}

Response: 201 Created
{
  "success": true,
  "message": "Cuenta creada exitosamente",
  "data": {
    "account": {
      "id": 1,
      "company_name": "Empresa Tech Solutions S.A.",
      "subscription_plan": "freemium",
      "max_locations": 1
    },
    "user": {
      "id": 1,
      "email": "admin@empresa.com",
      "full_name": "Juan Pérez",
      "user_type": "inventarista"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### POST /auth/login
Iniciar sesión
```json
Request:
{
  "email": "juan.perez@empresa.com",
  "password": "securePassword123"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "user": {
      "id": 15,
      "email": "juan.perez@empresa.com",
      "full_name": "Juan Pérez",
      "user_type": "employee",
      "is_blocked": false,
      "organization": {
        "id": 1,
        "name": "Empresa Tech Solutions S.A."
      }
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### POST /auth/facial-enrollment
Registrar datos faciales del usuario
```json
Request:
{
  "user_id": 15,
  "face_image": "base64_encoded_image_data"
}

Response: 200 OK
{
  "success": true,
  "message": "Datos faciales registrados exitosamente"
}
```

### POST /auth/facial-verify
Verificar identidad facial
```json
Request:
{
  "user_id": 15,
  "face_image": "base64_encoded_image_data"
}

Response: 200 OK
{
  "success": true,
  "verified": true,
  "confidence": 0.98
}
```

### POST /auth/register-employee
Registrar empleado adicional (Solo inventaristas)
```json
Request:
{
  "email": "empleado@empresa.com",
  "password": "securePassword123",
  "full_name": "María García"
}

Response: 201 Created
{
  "success": true,
  "message": "Empleado registrado exitosamente",
  "data": {
    "user": {
      "id": 2,
      "email": "empleado@empresa.com",
      "full_name": "María García",
      "user_type": "employee"
    }
  }
}
```

### POST /auth/logout
Cerrar sesión
```json
Response: 200 OK
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
```

---

## 👥 Usuarios

### GET /users/me
Obtener información del usuario autenticado
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 15,
    "email": "juan.perez@empresa.com",
    "full_name": "Juan Pérez",
    "user_type": "employee",
    "is_blocked": false,
    "organization": {
      "id": 1,
      "name": "Empresa Tech Solutions S.A."
    },
    "active_loans_count": 2,
    "pending_requests_count": 1
  }
}
```

### PUT /users/me
Actualizar perfil del usuario
```json
Request:
{
  "full_name": "Juan Carlos Pérez"
}

Response: 200 OK
{
  "success": true,
  "message": "Perfil actualizado exitosamente",
  "data": {
    "id": 15,
    "full_name": "Juan Carlos Pérez"
  }
}
```

### GET /users
Listar usuarios (Solo inventaristas)
```json
Query params: ?page=1&limit=20&user_type=employee&is_blocked=false

Response: 200 OK
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 15,
        "email": "juan.perez@empresa.com",
        "full_name": "Juan Pérez",
        "user_type": "employee",
        "is_blocked": false,
        "active_loans": 2,
        "created_at": "2026-01-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 156,
      "pages": 8
    }
  }
}
```

### PUT /users/:id/block
Bloquear/desbloquear usuario (Solo inventaristas)
```json
Request:
{
  "is_blocked": true,
  "blocked_reason": "Devolución tardía reiterada",
  "blocked_until": "2026-02-15"
}

Response: 200 OK
{
  "success": true,
  "message": "Usuario bloqueado exitosamente"
}
```

---

## 📦 Materiales

### GET /materials
Listar materiales
```json
Query params: ?page=1&limit=20&status=available&category_id=5&search=laptop

Response: 200 OK
{
  "success": true,
  "data": {
    "materials": [
      {
        "id": 101,
        "qr_code": "MAT-2026-0101",
        "name": "Laptop Dell Latitude 5420",
        "description": "Laptop para desarrollo",
        "brand": "Dell",
        "model": "Latitude 5420",
        "serial_number": "DL5420-2024-001",
        "status": "available",
        "condition": "good",
        "category": {
          "id": 5,
          "name": "Computadoras",
          "requires_facial_auth": true
        },
        "location": {
          "id": 3,
          "name": "Almacén Principal",
          "building": "Edificio A"
        },
        "image_url": "https://storage.pack-a-stock.com/materials/101.jpg"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

### GET /materials/:id
Obtener detalle de un material
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 101,
    "qr_code": "MAT-2026-0101",
    "name": "Laptop Dell Latitude 5420",
    "description": "Laptop para desarrollo",
    "brand": "Dell",
    "model": "Latitude 5420",
    "serial_number": "DL5420-2024-001",
    "acquisition_date": "2025-06-15",
    "acquisition_cost": 1200.00,
    "status": "available",
    "condition": "good",
    "notes": "Incluye cargador y mouse",
    "category": {
      "id": 5,
      "name": "Computadoras",
      "requires_facial_auth": true,
      "max_loan_days": 14
    },
    "location": {
      "id": 3,
      "name": "Almacén Principal",
      "building": "Edificio A",
      "room": "A-102"
    },
    "loan_history_count": 15,
    "current_loan": null
  }
}
```

### POST /materials
Crear nuevo material (Solo inventaristas)
```json
Request:
{
  "category_id": 5,
  "location_id": 3,
  "name": "Laptop HP ProBook 450",
  "description": "Laptop para uso académico",
  "brand": "HP",
  "model": "ProBook 450 G9",
  "serial_number": "HP450-2025-045",
  "acquisition_date": "2025-12-10",
  "acquisition_cost": 950.00,
  "condition": "good",
  "notes": "Incluye cargador"
}

Response: 201 Created
{
  "success": true,
  "message": "Material creado exitosamente",
  "data": {
    "id": 102,
    "qr_code": "MAT-2026-0102",
    "name": "Laptop HP ProBook 450",
    "status": "available"
  }
}
```

### PUT /materials/:id
Actualizar material (Solo inventaristas)
```json
Request:
{
  "location_id": 4,
  "condition": "fair",
  "notes": "Batería con menor capacidad"
}

Response: 200 OK
{
  "success": true,
  "message": "Material actualizado exitosamente"
}
```

### PUT /materials/:id/status
Cambiar estado del material (Solo inventaristas)
```json
Request:
{
  "status": "maintenance",
  "notes": "Requiere limpieza y mantenimiento preventivo"
}

Response: 200 OK
{
  "success": true,
  "message": "Estado del material actualizado"
}
```

### DELETE /materials/:id
Eliminar material (Solo inventaristas)
```json
Response: 200 OK
{
  "success": true,
  "message": "Material eliminado exitosamente"
}
```

### GET /materials/qr/:qrCode
Buscar material por código QR
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 101,
    "qr_code": "MAT-2026-0101",
    "name": "Laptop Dell Latitude 5420",
    "status": "available",
    "category": {
      "id": 5,
      "name": "Computadoras"
    }
  }
}
```

---

## 📋 Categorías

### GET /categories
Listar categorías
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 5,
      "name": "Computadoras",
      "description": "Laptops y computadoras de escritorio",
      "requires_facial_auth": true,
      "max_loan_days": 14,
      "materials_count": 45
    },
    {
      "id": 6,
      "name": "Proyectores",
      "description": "Proyectores multimedia",
      "requires_facial_auth": true,
      "max_loan_days": 3,
      "materials_count": 12
    }
  ]
}
```

### POST /categories
Crear categoría (Solo inventaristas)
```json
Request:
{
  "name": "Cámaras Fotográficas",
  "description": "Cámaras DSLR y mirrorless",
  "requires_facial_auth": true,
  "max_loan_days": 7
}

Response: 201 Created
{
  "success": true,
  "message": "Categoría creada exitosamente",
  "data": {
    "id": 7,
    "name": "Cámaras Fotográficas"
  }
}
```

### PUT /categories/:id
Actualizar categoría (Solo inventaristas)
```json
Request:
{
  "max_loan_days": 10
}

Response: 200 OK
{
  "success": true,
  "message": "Categoría actualizada exitosamente"
}
```

### DELETE /categories/:id
Eliminar categoría (Solo inventaristas)
```json
Response: 200 OK
{
  "success": true,
  "message": "Categoría eliminada exitosamente"
}
```

---

## 📍 Ubicaciones

### GET /locations
Listar ubicaciones
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 3,
      "name": "Almacén Principal",
      "building": "Edificio A",
      "floor": "Planta Baja",
      "room": "A-102",
      "materials_count": 78
    }
  ]
}
```

### POST /locations
Crear ubicación/almacén (Solo inventaristas)
```json
Request:
{
  "name": "Almacén Sucursal Norte",
  "building": "Edificio C",
  "floor": "Piso 2",
  "room": "C-205"
}

Response: 201 Created
{
  "success": true,
  "message": "Ubicación creada exitosamente",
  "data": {
    "id": 2,
    "name": "Almacén Sucursal Norte"
  }
}

// Error si se alcanza el límite (plan freemium)
Response: 403 Forbidden
{
  "success": false,
  "error": {
    "code": "LOCATION_LIMIT_REACHED",
    "message": "Has alcanzado el límite de almacenes para tu plan",
    "details": {
      "current_plan": "freemium",
      "max_locations": 1,
      "current_locations": 1,
      "upgrade_url": "/subscription/upgrade"
    }
  }
}
```

---

## 📝 Solicitudes de Préstamo

### GET /loan-requests
Listar solicitudes de préstamo
```json
Query params: ?status=pending&user_id=15

Response: 200 OK
{
  "success": true,
  "data": {
    "requests": [
      {
        "id": 45,
        "user": {
          "id": 15,
          "full_name": "Juan Pérez",
          "email": "juan.perez@empresa.com"
        },
        "request_date": "2026-01-14T10:30:00Z",
        "desired_pickup_date": "2026-01-16",
        "desired_return_date": "2026-01-23",
        "purpose": "Proyecto de investigación",
        "status": "pending",
        "items": [
          {
            "material_id": 101,
            "material_name": "Laptop Dell Latitude 5420",
            "material_qr": "MAT-2026-0101"
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 8,
      "pages": 1
    }
  }
}
```

### GET /loan-requests/:id
Obtener detalle de solicitud
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 45,
    "user": {
      "id": 15,
      "full_name": "Juan Pérez",
      "email": "juan.perez@empresa.com",
      "user_type": "employee"
    },
    "request_date": "2026-01-14T10:30:00Z",
    "desired_pickup_date": "2026-01-16",
    "desired_return_date": "2026-01-23",
    "purpose": "Proyecto de investigación sobre IoT",
    "status": "pending",
    "items": [
      {
        "id": 78,
        "material": {
          "id": 101,
          "qr_code": "MAT-2026-0101",
          "name": "Laptop Dell Latitude 5420",
          "status": "available",
          "category": {
            "name": "Computadoras",
            "requires_facial_auth": true
          }
        }
      }
    ]
  }
}
```

### POST /loan-requests
Crear solicitud de préstamo
```json
Request:
{
  "desired_pickup_date": "2026-01-16",
  "desired_return_date": "2026-01-23",
  "purpose": "Proyecto de investigación sobre IoT",
  "material_ids": [101, 105]
}

Response: 201 Created
{
  "success": true,
  "message": "Solicitud de préstamo creada exitosamente",
  "data": {
    "id": 45,
    "status": "pending",
    "items_count": 2
  }
}
```

### PUT /loan-requests/:id/approve
Aprobar solicitud (Solo inventaristas)
```json
Request:
{
  "review_notes": "Aprobado para proyecto de investigación"
}

Response: 200 OK
{
  "success": true,
  "message": "Solicitud aprobada exitosamente",
  "data": {
    "id": 45,
    "status": "approved"
  }
}
```

### PUT /loan-requests/:id/reject
Rechazar solicitud (Solo inventaristas)
```json
Request:
{
  "review_notes": "Materiales no disponibles en las fechas solicitadas"
}

Response: 200 OK
{
  "success": true,
  "message": "Solicitud rechazada",
  "data": {
    "id": 45,
    "status": "rejected"
  }
}
```

### DELETE /loan-requests/:id
Cancelar solicitud (Solo el usuario que la creó)
```json
Response: 200 OK
{
  "success": true,
  "message": "Solicitud cancelada exitosamente"
}
```

---

## 🔄 Préstamos

### GET /loans
Listar préstamos
```json
Query params: ?status=active&user_id=15&page=1

Response: 200 OK
{
  "success": true,
  "data": {
    "loans": [
      {
        "id": 89,
        "user": {
          "id": 15,
          "full_name": "Juan Pérez"
        },
        "material": {
          "id": 101,
          "qr_code": "MAT-2026-0101",
          "name": "Laptop Dell Latitude 5420"
        },
        "issued_at": "2026-01-10T14:00:00Z",
        "expected_return_date": "2026-01-17",
        "status": "active",
        "days_remaining": 2,
        "is_overdue": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 2,
      "pages": 1
    }
  }
}
```

### GET /loans/:id
Obtener detalle del préstamo
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 89,
    "loan_request_id": 45,
    "user": {
      "id": 15,
      "full_name": "Juan Pérez",
      "email": "juan.perez@empresa.com"
    },
    "material": {
      "id": 101,
      "qr_code": "MAT-2026-0101",
      "name": "Laptop Dell Latitude 5420",
      "brand": "Dell",
      "model": "Latitude 5420",
      "serial_number": "DL5420-2024-001"
    },
    "issued_by": {
      "id": 2,
      "full_name": "María López"
    },
    "issued_at": "2026-01-10T14:00:00Z",
    "expected_return_date": "2026-01-17",
    "facial_auth_verified": true,
    "facial_auth_at": "2026-01-10T14:00:00Z",
    "condition_on_pickup": "good",
    "status": "active",
    "extensions": []
  }
}
```

### POST /loans
Crear préstamo directo (Solo inventaristas)
```json
Request:
{
  "user_id": 15,
  "material_id": 101,
  "expected_return_date": "2026-01-17",
  "condition_on_pickup": "good",
  "facial_auth_verified": true
}

Response: 201 Created
{
  "success": true,
  "message": "Préstamo creado exitosamente",
  "data": {
    "id": 89,
    "status": "active",
    "expected_return_date": "2026-01-17"
  }
}
```

### POST /loans/from-request/:requestId
Crear préstamos desde solicitud aprobada (Solo inventaristas)
```json
Request:
{
  "items": [
    {
      "material_id": 101,
      "condition_on_pickup": "good",
      "facial_auth_verified": true
    },
    {
      "material_id": 105,
      "condition_on_pickup": "good",
      "facial_auth_verified": false
    }
  ]
}

Response: 201 Created
{
  "success": true,
  "message": "Préstamos creados exitosamente",
  "data": {
    "loans_created": 2,
    "loan_ids": [89, 90]
  }
}
```

### PUT /loans/:id/return
Registrar devolución (Solo inventaristas)
```json
Request:
{
  "condition_on_return": "good",
  "damage_notes": null
}

Response: 200 OK
{
  "success": true,
  "message": "Devolución registrada exitosamente",
  "data": {
    "id": 89,
    "status": "returned",
    "actual_return_date": "2026-01-16T10:30:00Z",
    "was_overdue": false
  }
}
```

### POST /loans/:id/extend
Solicitar extensión de préstamo
```json
Request:
{
  "new_return_date": "2026-01-24",
  "reason": "Requiero más tiempo para completar el proyecto"
}

Response: 201 Created
{
  "success": true,
  "message": "Solicitud de extensión enviada",
  "data": {
    "extension_id": 12,
    "status": "pending"
  }
}
```

### GET /loans/:id/extensions
Obtener extensiones de un préstamo
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 12,
      "loan_id": 89,
      "requested_at": "2026-01-15T09:00:00Z",
      "new_return_date": "2026-01-24",
      "reason": "Requiero más tiempo para completar el proyecto",
      "status": "pending"
    }
  ]
}
```

### PUT /loans/extensions/:id/approve
Aprobar extensión (Solo inventaristas)
```json
Request:
{
  "review_notes": "Extensión aprobada"
}

Response: 200 OK
{
  "success": true,
  "message": "Extensión aprobada exitosamente"
}
```

### PUT /loans/extensions/:id/reject
Rechazar extensión (Solo inventaristas)
```json
Request:
{
  "review_notes": "Material requerido por otro usuario"
}

Response: 200 OK
{
  "success": true,
  "message": "Extensión rechazada"
}
```

---

## 🔔 Notificaciones

### GET /notifications
Listar notificaciones del usuario
```json
Query params: ?is_read=false&page=1

Response: 200 OK
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 234,
        "type": "loan_approved",
        "title": "Solicitud Aprobada",
        "message": "Tu solicitud de préstamo ha sido aprobada",
        "related_loan_id": null,
        "related_request_id": 45,
        "is_read": false,
        "sent_at": "2026-01-14T15:30:00Z"
      },
      {
        "id": 235,
        "type": "return_reminder",
        "title": "Recordatorio de Devolución",
        "message": "Recuerda devolver Laptop Dell Latitude 5420 mañana",
        "related_loan_id": 89,
        "related_request_id": null,
        "is_read": false,
        "sent_at": "2026-01-15T08:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 2,
      "pages": 1
    },
    "unread_count": 2
  }
}
```

### PUT /notifications/:id/read
Marcar notificación como leída
```json
Response: 200 OK
{
  "success": true,
  "message": "Notificación marcada como leída"
}
```

### PUT /notifications/read-all
Marcar todas como leídas
```json
Response: 200 OK
{
  "success": true,
  "message": "Todas las notificaciones marcadas como leídas"
}
```

---

## 🏷️ Etiquetas QR

### GET /labels/templates
Listar plantillas de etiquetas (Solo inventaristas)
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Etiqueta Estándar",
      "template_type": "medium",
      "width_mm": 50,
      "height_mm": 30,
      "include_logo": true,
      "include_qr": true,
      "include_name": true,
      "is_default": true
    }
  ]
}
```

### POST /labels/generate
Generar etiqueta QR para material (Solo inventaristas)
```json
Request:
{
  "material_id": 101,
  "template_id": 1
}

Response: 200 OK
{
  "success": true,
  "message": "Etiqueta generada exitosamente",
  "data": {
    "label_url": "https://storage.pack-a-stock.com/labels/MAT-2026-0101.pdf",
    "qr_code": "MAT-2026-0101"
  }
}
```

### POST /labels/generate-batch
Generar etiquetas en lote (Solo inventaristas)
```json
Request:
{
  "material_ids": [101, 102, 103, 104, 105],
  "template_id": 1
}

Response: 200 OK
{
  "success": true,
  "message": "Etiquetas generadas exitosamente",
  "data": {
    "batch_url": "https://storage.pack-a-stock.com/labels/batch-2026-01-15.pdf",
    "labels_generated": 5
  }
}
```

---

## 📊 Reportes y Estadísticas

### GET /reports/dashboard
Obtener datos del dashboard (Solo inventaristas)
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "total_materials": 156,
    "available_materials": 98,
    "on_loan_materials": 45,
    "maintenance_materials": 8,
    "damaged_materials": 5,
    "active_loans": 45,
    "overdue_loans": 3,
    "pending_requests": 8,
    "blocked_users": 2,
    "loans_this_month": 87,
    "top_borrowed_materials": [
      {
        "material_id": 101,
        "material_name": "Laptop Dell Latitude 5420",
        "loan_count": 15
      }
    ],
    "top_borrowers": [
      {
        "user_id": 15,
        "user_name": "Juan Pérez",
        "loan_count": 8
      }
    ]
  }
}
```

### GET /reports/loans
Reporte de préstamos (Solo inventaristas)
```json
Query params: ?start_date=2026-01-01&end_date=2026-01-31&status=all&format=json

Response: 200 OK
{
  "success": true,
  "data": {
    "loans": [
      {
        "id": 89,
        "user_name": "Juan Pérez",
        "material_name": "Laptop Dell Latitude 5420",
        "issued_at": "2026-01-10T14:00:00Z",
        "expected_return_date": "2026-01-17",
        "actual_return_date": null,
        "status": "active",
        "days_overdue": 0
      }
    ],
    "summary": {
      "total_loans": 87,
      "active_loans": 45,
      "returned_loans": 39,
      "overdue_loans": 3,
      "average_loan_duration_days": 5.8
    }
  }
}
```

### GET /reports/materials-usage
Reporte de uso de materiales (Solo inventaristas)
```json
Query params: ?start_date=2026-01-01&end_date=2026-01-31&category_id=5

Response: 200 OK
{
  "success": true,
  "data": {
    "materials": [
      {
        "material_id": 101,
        "material_name": "Laptop Dell Latitude 5420",
        "category": "Computadoras",
        "total_loans": 15,
        "total_days_loaned": 75,
        "average_loan_duration": 5.0,
        "utilization_rate": 0.82
      }
    ]
  }
}
```

### GET /reports/user-activity
Reporte de actividad de usuarios (Solo inventaristas)
```json
Query params: ?start_date=2026-01-01&end_date=2026-01-31&user_type=employee

Response: 200 OK
{
  "success": true,
  "data": {
    "users": [
      {
        "user_id": 15,
        "user_name": "Juan Pérez",
        "user_type": "employee",
        "total_requests": 12,
        "approved_requests": 10,
        "rejected_requests": 2,
        "total_loans": 10,
        "active_loans": 2,
        "overdue_count": 0,
        "on_time_returns": 8
      }
    ]
  }
}
```

---

## 📱 Endpoints Específicos Mobile

### POST /mobile/scan-qr
Escanear código QR
```json
Request:
{
  "qr_code": "MAT-2026-0101"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "material": {
      "id": 101,
      "qr_code": "MAT-2026-0101",
      "name": "Laptop Dell Latitude 5420",
      "description": "Laptop para desarrollo",
      "status": "available",
      "category": {
        "id": 5,
        "name": "Computadoras",
        "requires_facial_auth": true,
        "max_loan_days": 14
      },
      "image_url": "https://storage.pack-a-stock.com/materials/101.jpg",
      "can_request": true
    }
  }
}
```

### GET /mobile/my-loans
Mis préstamos activos (Mobile)
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 89,
      "material": {
        "id": 101,
        "qr_code": "MAT-2026-0101",
        "name": "Laptop Dell Latitude 5420",
        "image_url": "https://storage.pack-a-stock.com/materials/101.jpg"
      },
      "issued_at": "2026-01-10T14:00:00Z",
      "expected_return_date": "2026-01-17",
      "status": "active",
      "days_remaining": 2,
      "is_overdue": false,
      "can_extend": true
    }
  ]
}
```

### GET /mobile/my-requests
Mis solicitudes (Mobile)
```json
Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": 45,
      "request_date": "2026-01-14T10:30:00Z",
      "desired_pickup_date": "2026-01-16",
      "desired_return_date": "2026-01-23",
      "status": "pending",
      "items_count": 2,
      "items": [
        {
          "material_name": "Laptop Dell Latitude 5420",
          "material_image": "https://storage.pack-a-stock.com/materials/101.jpg"
        }
      ]
    }
  ]
}
```

---

## 🔍 Búsqueda y Filtros

### GET /search
Búsqueda general
```json
Query params: ?q=laptop&type=materials

Response: 200 OK
{
  "success": true,
  "data": {
    "results": [
      {
        "type": "material",
        "id": 101,
        "name": "Laptop Dell Latitude 5420",
        "qr_code": "MAT-2026-0101",
        "status": "available"
      }
    ],
    "total": 1
  }
}
```

---

## ⚙️ Configuración

### GET /config/account
Obtener configuración de la cuenta/empresa
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Empresa Tech Solutions S.A.",
    "logo_url": "https://storage.pack-a-stock.com/logos/org-1.png",
    "email": "inventario@techsolutions.com",
    "settings": {
      "default_loan_days": 7,
      "max_active_loans_per_user": 5,
      "allow_extensions": true,
      "max_extensions_per_loan": 2,
      "block_on_overdue": true,
      "reminder_days_before_return": 1
    }
  }
}
```

### PUT /config/account
Actualizar configuración (Solo inventaristas)
```json
Request:
{
  "settings": {
    "default_loan_days": 10,
    "max_active_loans_per_user": 3
  }
}

Response: 200 OK
{
  "success": true,
  "message": "Configuración actualizada exitosamente"
}
```

---

## 🚨 Códigos de Error

### Códigos HTTP Estándar
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `500` - Internal Server Error

### Formato de Error
```json
{
  "success": false,
  "error": {
    "code": "MATERIAL_NOT_AVAILABLE",
    "message": "El material no está disponible para préstamo",
    "details": {
      "material_id": 101,
      "current_status": "on_loan"
    }
  }
}
```

### Códigos de Error Personalizados
- `USER_BLOCKED` - Usuario bloqueado
- `MATERIAL_NOT_AVAILABLE` - Material no disponible
- `FACIAL_AUTH_REQUIRED` - Autenticación facial requerida
- `FACIAL_AUTH_FAILED` - Autenticación facial fallida
- `MAX_LOANS_REACHED` - Límite de préstamos alcanzado
- `LOAN_OVERDUE` - Préstamo vencido
- `INVALID_QR_CODE` - Código QR inválido
- `EXTENSION_NOT_ALLOWED` - Extensión no permitida
- `INVALID_DATE_RANGE` - Rango de fechas inválido

---

## 🔄 Flujos de Trabajo Principales

### Flujo 1: Solicitud y Aprobación de Préstamo

1. **Usuario solicita préstamo** (Mobile)
   ```
   POST /loan-requests
   ```

2. **Inventarista revisa solicitud** (Web)
   ```
   GET /loan-requests
   GET /loan-requests/:id
   ```

3. **Inventarista aprueba** (Web)
   ```
   PUT /loan-requests/:id/approve
   ```

4. **Usuario recibe notificación** (Mobile)
   ```
   GET /notifications
   ```

5. **Inventarista crea préstamo al recoger** (Web)
   ```
   POST /loans/from-request/:requestId
   ```
   - Escanea QR del material
   - Verifica identidad facial (si aplica)
   - Registra condición del material

### Flujo 2: Devolución de Material

1. **Usuario lleva material** (Presencial)

2. **Inventarista escanea QR** (Web)
   ```
   GET /materials/qr/:qrCode
   ```

3. **Inventarista registra devolución** (Web)
   ```
   PUT /loans/:id/return
   ```
   - Verifica condición del material
   - Registra daños si aplica

4. **Usuario recibe confirmación** (Mobile)
   ```
   GET /notifications
   ```

### Flujo 3: Extensión de Préstamo

1. **Usuario solicita extensión** (Mobile)
   ```
   POST /loans/:id/extend
   ```

2. **Inventarista revisa** (Web)
   ```
   GET /loans/:id/extensions
   ```

3. **Inventarista aprueba/rechaza** (Web)
   ```
   PUT /loans/extensions/:id/approve
   // o
   PUT /loans/extensions/:id/reject
   ```

4. **Usuario recibe notificación** (Mobile)
   ```
   GET /notifications
   ```

---

## 📌 Notas de Implementación

### Autenticación
- Todos los endpoints (excepto `/auth/register` y `/auth/login`) requieren token JWT en el header:
  ```
  Authorization: Bearer <token>
  ```

### Permisos
- **Inventarista** (Owner/Admin): 
  - Acceso completo a toda la cuenta
  - Gestión de materiales, categorías, ubicaciones
  - Aprobación/rechazo de solicitudes
  - Creación de empleados adicionales
  - Gestión de suscripción
- **Empleados**: 
  - Solicitar préstamos
  - Ver sus propios préstamos activos
  - Solicitar extensiones
  - Escanear códigos QR
- **Aislamiento de datos**: Cada cuenta solo ve sus propios datos

### Paginación
- Endpoints de listado soportan paginación:
  ```
  ?page=1&limit=20
  ```

### Filtros Comunes
- `status` - Estado del recurso
- `search` - Búsqueda por texto
- `start_date` / `end_date` - Rango de fechas
- `category_id` - Filtro por categoría
- `user_id` - Filtro por usuario

### Rate Limiting
- Límite general: 100 requests/minuto por IP
- Endpoints de autenticación: 5 requests/minuto

### WebSockets (Opcional)
Para notificaciones en tiempo real:
```
wss://api.pack-a-stock.com/ws?token=<jwt_token>
```

---

## ✅ Checklist de Validación

### Base de Datos
- ✅ 12 tablas definidas
- ✅ Relaciones e índices configurados
- ✅ Campos para auditoría (created_at, updated_at)
- ✅ Soporte multi-organización
- ✅ Estados de materiales y préstamos
- ✅ Sistema de bloqueo de usuarios
- ✅ Registro de autenticación facial
- ✅ Plantillas de etiquetas

### API Endpoints
- ✅ Autenticación (registro, login, facial)
- ✅ Gestión de usuarios
- ✅ CRUD de materiales
- ✅ CRUD de categorías
- ✅ CRUD de ubicaciones
- ✅ Solicitudes de préstamo
- ✅ Gestión de préstamos
- ✅ Extensiones de préstamo
- ✅ Notificaciones
- ✅ Generación de etiquetas QR
- ✅ Reportes y estadísticas
- ✅ Endpoints específicos para mobile
- ✅ Búsqueda y filtros

### Funcionalidades
- ✅ Código QR individual por material
- ✅ Autenticación facial para artículos caros
- ✅ Sistema de aprobación/rechazo
- ✅ Control de retrasos y bloqueos
- ✅ Extensiones de préstamo
- ✅ Notificaciones push
- ✅ Historial de préstamos
- ✅ Auditoría completa
- ✅ Multi-organización
- ✅ Reportes y dashboards

---

## Configuración de Servidor

### Variables de Entorno (.env)

```bash
# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
ALLOWED_HOSTS=api.pack-a-stock.com,localhost
CORS_ALLOWED_ORIGINS=https://app.pack-a-stock.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/pack_a_stock_db
DB_NAME=pack_a_stock_db
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# AWS S3 / Cloud Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=pack-a-stock-media
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=
AWS_DEFAULT_ACL=public-read

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email (opcional)
EMAIL_BACKEND=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Sentry (monitoreo de errores)
SENTRY_DSN=
```

### Estructura de Buckets S3

```
pack-a-stock-media/
├── logos/                    # Logos de empresas para etiquetas
│   └── {account_id}/
│       └── logo.png
├── materials/                # Imágenes de materiales
│   └── {account_id}/
│       └── {material_id}.jpg
├── qr-codes/                 # Códigos QR generados
│   └── {account_id}/
│       └── {material_id}.png
└── labels/                   # Etiquetas PDF generadas
    └── {account_id}/
        ├── {material_id}.pdf
        └── batch-{timestamp}.pdf
```

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./Pack-a-Stock
    command: gunicorn pack_a_stock_api.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./Pack-a-Stock:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    build: ./Pack-a-Stock
    command: celery -A pack_a_stock_api worker -l info
    volumes:
      - ./Pack-a-Stock:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery-beat:
    build: ./Pack-a-Stock
    command: celery -A pack_a_stock_api beat -l info
    volumes:
      - ./Pack-a-Stock:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./Front_End_SaaS/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Configuración Nginx (nginx.conf)

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name app.pack-a-stock.com;

    # Frontend PWA
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin Django
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }
}
```

### Configuración PWA

**Frontend vite.config.ts**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Pack-a-Stock',
        short_name: 'Pack-a-Stock',
        description: 'Sistema de gestión de préstamos de materiales',
        theme_color: '#ffffff',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.pack-a-stock\.com\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300
              }
            }
          }
        ]
      }
    })
  ]
})
```

### Django Settings para Producción

**settings.py**
```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
}

# AWS S3 Storage
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# Storage backends
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (uploaded to S3)
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# Security
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
```

---

**¿Qué te parece este diseño completo? ¿Hay algo que quieras modificar o agregar? 💙**
