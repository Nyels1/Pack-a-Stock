# Base de Datos - Pack-a-Stock

## Estructura Completa de Tablas SQL

### 1. ACCOUNTS (Cuentas/Empresas)

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    
    -- Dirección completa
    street VARCHAR(255) NOT NULL,
    exterior_number VARCHAR(50) NOT NULL,
    interior_number VARCHAR(50),
    neighborhood VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) DEFAULT 'México',
    
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    
    -- Suscripción
    subscription_plan VARCHAR(50) DEFAULT 'freemium', -- 'freemium', 'premium'
    max_locations INTEGER DEFAULT 1,  -- Freemium: 1, Premium: -1 (ilimitado)
    max_users INTEGER DEFAULT 5,      -- Freemium: 5, Premium: -1 (ilimitado)
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_accounts_is_active ON accounts(is_active);
CREATE INDEX idx_accounts_subscription_plan ON accounts(subscription_plan);
```

### 2. USERS (Usuarios)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    
    user_type VARCHAR(50) NOT NULL, -- 'inventarista', 'employee'
    
    -- Autenticación facial (futuro)
    face_encoding TEXT,
    
    -- Bloqueos por préstamos tardíos
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_reason TEXT,
    blocked_until TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_users_account ON users(account_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_is_blocked ON users(is_blocked);
```

### 3. CATEGORIES (Categorías de Materiales)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Consumibles: se manejan por stock y no se devuelven
    is_consumable BOOLEAN DEFAULT FALSE,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_id, name)
);

-- Índices
CREATE INDEX idx_categories_account_active ON categories(account_id, is_active);
CREATE INDEX idx_categories_account_name ON categories(account_id, name);
```

### 4. LOCATIONS (Ubicaciones/Almacenes)

```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Dirección completa
    street VARCHAR(255) NOT NULL,
    exterior_number VARCHAR(50) NOT NULL,
    interior_number VARCHAR(50),
    neighborhood VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) DEFAULT 'México',
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_locations_account_active ON locations(account_id, is_active);
CREATE INDEX idx_locations_account_name ON locations(account_id, name);
```

### 5. MATERIALS (Materiales/Equipos)

```sql
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE PROTECT,
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    
    -- Información básica
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    barcode VARCHAR(100),
    
    -- Código QR único (individual para regulares, por lote para consumibles)
    qr_code VARCHAR(100) UNIQUE NOT NULL,
    qr_image VARCHAR(200), -- Ruta a imagen PNG del QR en S3
    
    -- Inventario
    quantity INTEGER DEFAULT 1,           -- Cantidad total
    available_quantity INTEGER DEFAULT 1, -- Cantidad disponible
    unit_of_measure VARCHAR(50) DEFAULT 'unit', -- 'unit', 'box', 'kg', etc.
    min_stock_level INTEGER DEFAULT 0,    -- Alerta de stock bajo
    reorder_quantity INTEGER DEFAULT 0,   -- Cantidad para reordenar
    
    -- Imagen del material (S3)
    image_url VARCHAR(500),
    
    -- Estado
    status VARCHAR(50) DEFAULT 'available', -- 'available', 'on_loan', 'maintenance', 'damaged', 'retired'
    is_available_for_loan BOOLEAN DEFAULT TRUE,
    requires_facial_auth BOOLEAN DEFAULT FALSE,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_materials_account_active ON materials(account_id, is_active);
CREATE INDEX idx_materials_account_category ON materials(account_id, category_id);
CREATE INDEX idx_materials_account_location ON materials(account_id, location_id);
CREATE INDEX idx_materials_qr_code ON materials(qr_code);
CREATE INDEX idx_materials_sku ON materials(sku);
CREATE INDEX idx_materials_status ON materials(status);
CREATE INDEX idx_materials_available_for_loan ON materials(is_available_for_loan);

-- Nota: is_consumable se determina por category.is_consumable (propiedad calculada)
```

### 6. LOAN_REQUESTS (Solicitudes de Préstamo)

```sql
CREATE TABLE loan_requests (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Fechas
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    desired_pickup_date DATE NOT NULL,
    desired_return_date DATE NOT NULL,
    
    purpose TEXT, -- Motivo del préstamo
    
    -- Estado y revisión
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    reviewed_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_loan_requests_account_status ON loan_requests(account_id, status);
CREATE INDEX idx_loan_requests_requester_status ON loan_requests(requester_id, status);
CREATE INDEX idx_loan_requests_desired_pickup ON loan_requests(desired_pickup_date);
CREATE INDEX idx_loan_requests_status ON loan_requests(status);
```

### 7. LOAN_REQUEST_ITEMS (Items de Solicitud)

```sql
CREATE TABLE loan_request_items (
    id SERIAL PRIMARY KEY,
    loan_request_id INTEGER NOT NULL REFERENCES loan_requests(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    
    quantity_requested INTEGER DEFAULT 1, -- Para consumibles
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(loan_request_id, material_id)
);

-- Índices
CREATE INDEX idx_loan_request_items_loan_request ON loan_request_items(loan_request_id);
CREATE INDEX idx_loan_request_items_material ON loan_request_items(material_id);
```

### 8. LOANS (Préstamos Activos)

```sql
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    loan_request_id INTEGER REFERENCES loan_requests(id) ON DELETE SET NULL,
    
    -- Usuarios involucrados
    borrower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issued_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    returned_to_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Material prestado
    material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    quantity_loaned INTEGER DEFAULT 1,
    quantity_returned INTEGER DEFAULT 0,
    
    -- Consumibles (no se devuelven)
    is_consumable_loan BOOLEAN DEFAULT FALSE,
    
    -- Fechas
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_return_date DATE,           -- NULL para consumibles
    actual_return_date TIMESTAMP,
    
    -- Autenticación facial
    facial_auth_verified BOOLEAN DEFAULT FALSE,
    facial_auth_at TIMESTAMP,
    
    -- Firmas digitales (base64)
    pickup_signature TEXT,
    return_signature TEXT,
    
    -- Condiciones del material
    condition_on_pickup VARCHAR(50) DEFAULT 'good', -- 'excellent', 'good', 'fair', 'poor', 'damaged'
    condition_on_return VARCHAR(50),
    damage_notes TEXT,
    
    -- Estado
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'returned', 'overdue', 'lost'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_loans_account_status ON loans(account_id, status);
CREATE INDEX idx_loans_borrower_status ON loans(borrower_id, status);
CREATE INDEX idx_loans_material_status ON loans(material_id, status);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_expected_return ON loans(expected_return_date);
CREATE INDEX idx_loans_loan_request ON loans(loan_request_id);
```

### 9. LOAN_EXTENSIONS (Extensiones de Préstamo)

```sql
CREATE TABLE loan_extensions (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    requested_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Solicitud
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    new_return_date DATE NOT NULL,
    reason TEXT NOT NULL,
    
    -- Revisión
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    reviewed_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_loan_extensions_loan_status ON loan_extensions(loan_id, status);
CREATE INDEX idx_loan_extensions_status ON loan_extensions(status);
```

---

## Resumen de Relaciones

```
accounts (1) ----< (N) users
accounts (1) ----< (N) categories
accounts (1) ----< (N) locations
accounts (1) ----< (N) materials
accounts (1) ----< (N) loan_requests
accounts (1) ----< (N) loans

categories (1) ----< (N) materials
locations (1) ----< (N) materials

users (1) ----< (N) loan_requests (requester)
users (1) ----< (N) loan_requests (reviewer)
users (1) ----< (N) loans (borrower)
users (1) ----< (N) loans (issued_by)
users (1) ----< (N) loans (returned_to)
users (1) ----< (N) loan_extensions (requester)
users (1) ----< (N) loan_extensions (reviewer)

loan_requests (1) ----< (N) loan_request_items
loan_requests (1) ----< (N) loans

materials (1) ----< (N) loan_request_items
materials (1) ----< (N) loans

loans (1) ----< (N) loan_extensions
```

---

## Reglas de Negocio Importantes

### Consumibles vs Materiales Regulares

**Consumibles** (`category.is_consumable = TRUE`):
- Se manejan por **stock** (cantidad)
- **No se devuelven** (se consumen al entregarlos)
- `loan.is_consumable_loan = TRUE`
- `loan.expected_return_date = NULL`
- Al aprobar préstamo: `material.available_quantity -= quantity_loaned`
- `loan.status` se marca como `'returned'` automáticamente
- QR por **lote** (mismo QR para todas las unidades)

**Materiales Regulares** (`category.is_consumable = FALSE`):
- Préstamo **individual**
- **Sí se devuelven**
- `loan.is_consumable_loan = FALSE`
- `loan.expected_return_date` requerida
- Control de estado: `active`, `overdue`, `returned`
- QR **individual** por material

### Planes de Suscripción

**Freemium**:
- `max_locations = 1` (1 almacén)
- `max_users = 5` (5 usuarios)

**Premium**:
- `max_locations = -1` (ilimitado)
- `max_users = -1` (ilimitado)

### Bloqueos Automáticos

Cuando un usuario devuelve materiales con retraso reiterado:
- `user.is_blocked = TRUE`
- `user.blocked_reason = "Devolución tardía reiterada"`
- `user.blocked_until = fecha_de_desbloqueo`

---

## Próximos Pasos (Opcional - NO implementado)

### AuditLogs (Para auditoría)
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    changes JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### LabelTemplates (Para etiquetas personalizadas)
```sql
CREATE TABLE label_templates (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    name VARCHAR(255),
    logo_url VARCHAR(500),
    layout JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
