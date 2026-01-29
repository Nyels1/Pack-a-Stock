# Pack-a-Stock Backend API

Sistema de gestion de inventario y prestamos desarrollado con Django REST Framework.

## Estado del Proyecto

**VERSION:** 1.0.0  
**ESTADO:** Modelos completados y probados (11/11)  
**FECHA:** 29 de Enero, 2026

## Inicio Rapido

### Requisitos Previos

- Python 3.13+
- PostgreSQL 14+ (produccion) o SQLite (desarrollo)
- pip

### Instalacion

1. Clonar el repositorio
```bash
git clone <repository-url>
cd Pack-a-Stock
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar migraciones
```bash
python manage.py migrate
```

6. Crear superadmin
```bash
python manage.py create_superadmin
```

7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## Credenciales de Prueba

**Superadmin:**
- Email: admin
- Contrasena: 12345

**IMPORTANTE:** Cambiar en produccion

## Estructura del Proyecto

```
Pack-a-Stock/
├── accounts/          # Gestion de cuentas y usuarios
├── materials/         # Gestion de inventario
├── loans/            # Gestion de prestamos
├── audit/            # Registros de auditoria
├── labels/           # Plantillas de etiquetas QR
├── pack_a_stock_api/ # Configuracion principal
└── BACKEND_DOCS.md   # Documentacion completa
```

## Modulos

### accounts
- Account: Empresas/organizaciones (multi-tenancy)
- User: Usuarios del sistema (inventaristas y empleados)

### materials
- Category: Categorias de materiales
- Location: Almacenes/ubicaciones fisicas
- Material: Equipos y materiales (consumibles y no-consumibles)

### loans
- LoanRequest: Solicitudes de prestamo
- LoanRequestItem: Items en solicitudes
- Loan: Prestamos activos
- LoanExtension: Extensiones de prestamos

### audit
- AuditLog: Registro de auditoria de todas las acciones del sistema

### labels
- LabelTemplate: Plantillas personalizadas para etiquetas QR

## Caracteristicas Principales

- Multi-tenancy (soporte para multiples empresas)
- Diferenciacion automatica: materiales consumibles vs no-consumibles
- Generacion automatica de codigos QR unicos
- Sistema de prestamos con aprobaciones
- Extensiones de prestamos
- Autenticacion facial (preparada)
- Firmas digitales en transacciones
- Control de stock con alertas
- API REST completa

## Tecnologias

- Django 5.0
- Django REST Framework 3.14.0
- PostgreSQL / SQLite
- JWT Authentication
- Python 3.13

## Documentacion

Consulta [BACKEND_DOCS.md](BACKEND_DOCS.md) para documentacion completa de:
- Todos los modelos y sus campos
- Metodos y propiedades
- Configuracion del proyecto
- Resultados de pruebas
- Notas tecnicas

## Pruebas

Todos los modelos han sido probados exhaustivamente:

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
