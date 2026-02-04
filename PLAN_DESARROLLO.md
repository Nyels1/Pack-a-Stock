# PLAN DE DESARROLLO - PACK-A-STOCK WEB (INVENTARISTAS)

## CONTEXTO DEL PROYECTO

Pack-a-Stock es un sistema SaaS multi-tenant para gestión de inventarios y préstamos de materiales empresariales. 

**IMPORTANTE:** La aplicación WEB es EXCLUSIVAMENTE para INVENTARISTAS (administradores). Los empleados solicitan préstamos desde una APP MÓVIL separada. En la web NO se solicitan préstamos, solo se ADMINISTRAN.

### Modelo de Negocio
- **Multi-tenant:** Cada empresa (Account) tiene datos aislados
- **Planes:** Freemium (1 ubicación, 5 usuarios) / Premium (ilimitado)
- **Usuarios web:** Solo inventaristas (rol administrativo)
- **Usuarios mobile:** Empleados que solicitan materiales (NO acceden a la web)

### Flujo Principal
1. **Mobile:** Empleado solicita préstamo de materiales mediante app móvil
2. **Web:** Inventarista revisa solicitud y aprueba/rechaza
3. **Web:** Inventarista entrega material (escanea QR, registra firma digital)
4. **Web:** Inventarista recibe devolución (escanea QR, verifica condición, registra firma)

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

## STACK TECNOLÓGICO FRONTEND

### Framework Base
- **Next.js 14+** (App Router)
  - React 18+
  - TypeScript
  - Server Components + Client Components

### UI y Estilos
- **Tailwind CSS** (utility-first CSS)
- **Shadcn/ui** (componentes base reutilizables)
  - Buttons, Modals, Dropdowns, etc.
- **Lucide Icons** o **Heroicons** (iconografía consistente)

### Gestión de Estado
- **Zustand** (estado global ligero)
- **TanStack Query (React Query)** (cache y sincronización de datos)

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

### Autenticación
- **JWT** en httpOnly cookies
- Middleware de Next.js para proteger rutas

### Notificaciones
- **react-hot-toast** o **sonner** (toast notifications)

### Date Handling
- **date-fns** (manipulación de fechas)

---

## ESTRUCTURA DE CARPETAS RECOMENDADA

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── recuperar-password/
│   ├── (dashboard)/
│   │   ├── layout.tsx (sidebar + header)
│   │   ├── page.tsx (dashboard principal)
│   │   ├── materiales/
│   │   │   ├── page.tsx
│   │   │   ├── nuevo/
│   │   │   ├── [id]/
│   │   │   └── categorias/
│   │   ├── solicitudes/
│   │   ├── prestamos/
│   │   ├── extensiones/
│   │   ├── usuarios/
│   │   ├── reportes/
│   │   ├── etiquetas/
│   │   └── configuracion/
│   └── api/ (route handlers si es necesario)
├── components/
│   ├── ui/ (shadcn components)
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
│   ├── api.ts (axios instance + endpoints)
│   ├── auth.ts (autenticación helpers)
│   ├── utils.ts (utilidades generales)
│   └── constants.ts (constantes globales)
├── hooks/
│   ├── useAuth.ts
│   ├── useMaterials.ts
│   ├── useLoans.ts
│   └── useQRScanner.ts
├── store/
│   └── authStore.ts (Zustand store)
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

**Backend:**
- [x] Modelos de base de datos completos
- [x] API REST funcionando
- [x] Autenticación JWT implementada
- [x] Documentación de endpoints

**Frontend (por hacer):**
- [ ] Inicializar proyecto Next.js 14
- [ ] Configurar Tailwind CSS + Shadcn/ui
- [ ] Configurar TypeScript
- [ ] Instalar dependencias necesarias
- [ ] Crear estructura de carpetas
- [ ] Configurar variables de entorno

---

## ¿POR DÓNDE EMPEZAMOS?

**Opción 1: Setup del proyecto (RECOMENDADO)**
- Crear proyecto Next.js
- Instalar y configurar todas las dependencias
- Configurar Tailwind + Shadcn
- Crear layout base (Sidebar + Header)

**Opción 2: Prototipo visual rápido**
- Crear wireframes/mockups en Figma
- Validar flujos de usuario
- Ajustar antes de programar

**Opción 3: Implementación directa**
- Empezar con Login + Dashboard
- Ir construyendo componente por componente

---

## COMANDOS PARA INICIAR

```bash
# Crear proyecto Next.js
npx create-next-app@latest frontend --typescript --tailwind --app

# Instalar Shadcn/ui
npx shadcn-ui@latest init

# Instalar dependencias adicionales
npm install zustand @tanstack/react-query axios zod react-hook-form @hookform/resolvers
npm install date-fns lucide-react recharts react-hot-toast
npm install @zxing/browser react-signature-canvas
npm install @tanstack/react-table

# Instalar tipos
npm install -D @types/node @types/react @types/react-dom
```

---

¿Qué opción prefieres para empezar?
