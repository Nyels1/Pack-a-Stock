# Pack-a-Stock API - FASE 1: Autenticación

## Servidor corriendo en: http://127.0.0.1:8000

## Endpoints Disponibles

### 1. Registro de Cuenta (Inventarista)
Crea una nueva cuenta de empresa y el primer usuario inventarista.

**POST** `/api/auth/register/`

**Body:**
```json
{
  "email": "admin@empresa.com",
  "password": "password123",
  "full_name": "Juan Pérez",
  "company_name": "Mi Empresa S.A.",
  "company_email": "contacto@empresa.com",
  "street": "Av. Principal",
  "exterior_number": "123",
  "interior_number": "A",
  "neighborhood": "Centro",
  "postal_code": "12345",
  "city": "Ciudad de México",
  "state": "CDMX",
  "country": "México",
  "phone": "5551234567",
  "subscription_plan": "freemium"
}
```

**Response 201:**
```json
{
  "account": {
    "id": 1,
    "company_name": "Mi Empresa S.A.",
    "email": "contacto@empresa.com",
    "subscription_plan": "freemium",
    "max_locations": 1,
    "max_users": 5,
    ...
  },
  "user": {
    "id": 1,
    "email": "admin@empresa.com",
    "full_name": "Juan Pérez",
    "user_type": "inventarista",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 2. Login
Iniciar sesión con email y contraseña.

**POST** `/api/auth/login/`

**Body:**
```json
{
  "email": "admin@empresa.com",
  "password": "password123"
}
```

**Response 200:**
```json
{
  "user": {
    "id": 1,
    "email": "admin@empresa.com",
    "full_name": "Juan Pérez",
    "user_type": "inventarista",
    "account": {
      "id": 1,
      "company_name": "Mi Empresa S.A.",
      ...
    }
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 3. Logout
Cerrar sesión (invalidar refresh token).

**POST** `/api/auth/logout/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

---

### 4. Obtener Perfil del Usuario Actual
Obtener información del usuario autenticado.

**GET** `/api/users/me/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "id": 1,
  "email": "admin@empresa.com",
  "full_name": "Juan Pérez",
  "user_type": "inventarista",
  "account": {
    "id": 1,
    "company_name": "Mi Empresa S.A.",
    ...
  },
  ...
}
```

---

### 5. Actualizar Perfil
Actualizar información del usuario actual.

**PUT** `/api/users/me/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "full_name": "Juan Carlos Pérez"
}
```

---

### 6. Crear Empleado (Solo Inventarista)
Crear un nuevo empleado en la cuenta.

**POST** `/api/users/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "email": "empleado@empresa.com",
  "password": "password123",
  "full_name": "María García"
}
```

**Response 201:**
```json
{
  "id": 2,
  "email": "empleado@empresa.com",
  "full_name": "María García",
  "user_type": "employee",
  ...
}
```

**Error 403 (si alcanzó límite de usuarios):**
```json
{
  "error": "Has alcanzado el límite de 5 usuarios para tu plan"
}
```

---

### 7. Listar Usuarios de la Cuenta
Listar todos los usuarios de tu cuenta.

**GET** `/api/users/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "email": "admin@empresa.com",
      "full_name": "Juan Pérez",
      "user_type": "inventarista",
      ...
    },
    {
      "id": 2,
      "email": "empleado@empresa.com",
      "full_name": "María García",
      "user_type": "employee",
      ...
    }
  ]
}
```

---

### 8. Bloquear/Desbloquear Usuario (Solo Inventarista)
Bloquear o desbloquear un usuario.

**PUT** `/api/users/{id}/block/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "is_blocked": true,
  "blocked_reason": "Devolución tardía reiterada",
  "blocked_until": "2026-02-15T00:00:00Z"
}
```

**Response 200:**
```json
{
  "id": 2,
  "email": "empleado@empresa.com",
  "is_blocked": true,
  "blocked_reason": "Devolución tardía reiterada",
  "blocked_until": "2026-02-15T00:00:00Z",
  ...
}
```

---

### 9. Actualizar Información de la Cuenta
Actualizar datos de la empresa.

**PUT** `/api/accounts/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body:**
```json
{
  "company_name": "Mi Empresa S.A. de C.V.",
  "phone": "5559876543"
}
```

---

## Validaciones Implementadas

### Límites por Plan

**Freemium:**
- max_locations: 1
- max_users: 5

**Premium:**
- max_locations: ilimitado (-1)
- max_users: ilimitado (-1)

### Errores Comunes

**400 Bad Request:**
```json
{
  "email": ["Este email ya está registrado"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

**403 Forbidden:**
```json
{
  "error": "Solo inventaristas pueden crear usuarios"
}
```

---

## Próximos Pasos

- FASE 2: Gestión de Inventario (materiales, categorías, ubicaciones)
- FASE 3: Sistema de Etiquetas QR
- FASE 4: Sistema de Préstamos
