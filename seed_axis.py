"""
Seed script para Pack-a-Stock -- Empresa: Axis
"""
import random
from datetime import date, timedelta, datetime
from django.utils import timezone

from accounts.models import Account, User
from materials.models import Category, Location, Material
from loans.models import LoanRequest, LoanRequestItem, Loan

print("=" * 60)
print("Iniciando seed para AXIS...")
print("=" * 60)

# --- 1. CUENTA AXIS ---
account, _ = Account.objects.get_or_create(
    email='axis@axisconstruccion.mx',
    defaults={
        'company_name': 'Axis',
        'street': 'Av. Insurgentes Sur',
        'exterior_number': '1457',
        'neighborhood': 'Insurgentes Mixcoac',
        'postal_code': '03920',
        'city': 'Ciudad de Mexico',
        'state': 'CDMX',
        'country': 'Mexico',
        'phone': '55 4321 8800',
        'subscription_plan': 'annual',
        'max_users': -1,
        'max_locations': -1,
    }
)
print("OK Account: " + account.company_name + " (code=" + account.company_code + ")")

# --- 2. INVENTARISTA PRINCIPAL ---
inv, _ = User.objects.get_or_create(
    email='inventario@axisconstruccion.mx',
    defaults={
        'account': account,
        'full_name': 'Inventarista Axis',
        'user_type': 'inventarista',
        'is_active': True,
    }
)
inv.set_password('axis2024')
inv.save()
print("OK Inventarista: " + inv.email + " / pass: axis2024")

# --- 3. USUARIO MOVIL --- ERNESTO GARCIA VALENZUELA ---
ernesto, _ = User.objects.get_or_create(
    email='ernesto.garcia@axisconstruccion.mx',
    defaults={
        'account': account,
        'full_name': 'Ernesto Garcia Valenzuela',
        'user_type': 'employee',
        'is_active': True,
    }
)
ernesto.set_password('ernesto123')
ernesto.save()
print("OK Empleado movil: " + ernesto.email + " / pass: ernesto123")

# --- 4. EMPLEADOS ADICIONALES ---
empleados_data = [
    ('carlos.mendoza@axisconstruccion.mx',  'Carlos Mendoza Ruiz'),
    ('sofia.reyes@axisconstruccion.mx',     'Sofia Reyes Herrera'),
    ('miguel.angel@axisconstruccion.mx',    'Miguel Angel Castillo'),
    ('diana.flores@axisconstruccion.mx',    'Diana Flores Vega'),
    ('roberto.juarez@axisconstruccion.mx',  'Roberto Juarez Morales'),
]
empleados = []
for email, nombre in empleados_data:
    u, _ = User.objects.get_or_create(
        email=email,
        defaults={
            'account': account,
            'full_name': nombre,
            'user_type': 'employee',
            'is_active': True,
        }
    )
    u.set_password('empleado123')
    u.save()
    empleados.append(u)
    print("  + Empleado: " + nombre)

# --- 5. UBICACIONES ---
locs_data = [
    ('Bodega Central',    'Almacen principal de herramientas y equipos',
     'Av. Insurgentes Sur', '1457', 'Insurgentes Mixcoac', '03920', 'CDMX'),
    ('Almacen Norte',     'Almacen de materiales de construccion pesados',
     'Calle Moctezuma',   '320',   'Industrial Vallejo',   '07700', 'CDMX'),
    ('Taller Electrico',  'Area de herramientas electricas y calibracion',
     'Blvd. Puerto Aereo','98',    'Moctezuma 2a Secc',    '15530', 'CDMX'),
]
locations = []
for nombre, desc, calle, num, col, cp, ciudad in locs_data:
    loc, _ = Location.objects.get_or_create(
        account=account,
        name=nombre,
        defaults={
            'description': desc,
            'street': calle,
            'exterior_number': num,
            'neighborhood': col,
            'postal_code': cp,
            'city': ciudad,
            'state': 'Ciudad de Mexico',
            'country': 'Mexico',
        }
    )
    locations.append(loc)
    print("  + Ubicacion: " + nombre)

# --- 6. CATEGORIAS ---
cats_data = [
    ('Herramienta Manual',         'Martillos, llaves, desarmadores, etc.',    False),
    ('Herramienta Electrica',      'Taladros, amoladoras, sierras, etc.',      False),
    ('Equipo de Medicion',         'Cintas, niveles, teodolitos, etc.',         False),
    ('Equipo de Proteccion (EPP)', 'Cascos, guantes, arneses, lentes, etc.',   False),
    ('Consumibles Obra',           'Tornillos, tuercas, cintas, solventes.',    True),
    ('Material Electrico',         'Cables, conectores, canaletas, fusibles.',  True),
]
categories = {}
for nombre, desc, consumible in cats_data:
    cat, _ = Category.objects.get_or_create(
        account=account,
        name=nombre,
        defaults={'description': desc, 'is_consumable': consumible}
    )
    categories[nombre] = cat
    print("  + Categoria: " + nombre)

# --- 7. MATERIALES ---
materiales_data = [
    # (nombre, cat_key, loc_idx, qty, avail, unidad, serie, desc)
    # Herramienta Manual
    ('Martillo de Bola 500g',      'Herramienta Manual',         0,  5,  5,  'unit', 'MRT-001', 'Martillo de bola, mango fibra de vidrio'),
    ('Llave Ajustable 12"',        'Herramienta Manual',         0,  8,  8,  'unit', 'LLV-001', 'Llave ajustable Truper 12 pulgadas'),
    ('Juego Desarmadores 6 pzas',  'Herramienta Manual',         0,  4,  4,  'set',  'DSA-001', 'Set planos y cruz, mango ergonomico'),
    ('Pinzas de Electricista',     'Herramienta Manual',         0,  6,  5,  'unit', 'PNZ-001', 'Pinzas aisladas 1000V'),
    ('Cinta Metrica 5m',           'Herramienta Manual',         0, 10,  9,  'unit', 'CTM-001', 'Cinta Truper 5m con freno'),
    # Herramienta Electrica
    ('Taladro Percutor 1/2"',      'Herramienta Electrica',      1,  6,  4,  'unit', 'TAL-001', 'Taladro DeWalt 20V Max, baterias incluidas'),
    ('Amoladora Angular 4.5"',     'Herramienta Electrica',      1,  4,  3,  'unit', 'AML-001', 'Amoladora Bosch 850W, disco abrasivo'),
    ('Sierra Circular 7.25"',      'Herramienta Electrica',      1,  3,  2,  'unit', 'SRR-001', 'Sierra Skil 1800W con guia paralela'),
    ('Rotomartillo SDS-Plus',      'Herramienta Electrica',      2,  4,  4,  'unit', 'RTM-001', 'Rotomartillo Makita 800W, set de brocas'),
    ('Pistola de Calor',           'Herramienta Electrica',      2,  2,  2,  'unit', 'PST-001', 'Pistola calor 1800W, temperatura variable'),
    # Equipo de Medicion
    ('Nivel de Burbuja 120cm',     'Equipo de Medicion',         0,  6,  6,  'unit', 'NVL-001', 'Nivel Stanley 3 burbujas, aluminio'),
    ('Multimetro Digital',         'Equipo de Medicion',         2,  5,  4,  'unit', 'MLT-001', 'Multimetro Fluke 117, True RMS'),
    ('Teodolito Optico',           'Equipo de Medicion',         0,  2,  2,  'unit', 'TDL-001', 'Teodolito Wild T1, precision 1 minuto'),
    ('Detector de Metales/Cables', 'Equipo de Medicion',         2,  3,  3,  'unit', 'DTC-001', 'Detector Bosch D-Tect 120, AC y metales'),
    # EPP
    ('Casco de Seguridad',         'Equipo de Proteccion (EPP)', 0, 20, 18,  'unit', None,      'Casco 3M H-700, ala completa, blanco'),
    ('Arnes Anticaida',            'Equipo de Proteccion (EPP)', 0,  8,  7,  'unit', 'ARN-001', 'Arnes Miller, 5 puntos, talla unica'),
    ('Guantes de Trabajo (par)',   'Equipo de Proteccion (EPP)', 0, 30, 25,  'unit', None,      'Guantes vaqueta, resistentes a corte'),
    ('Lentes de Seguridad',        'Equipo de Proteccion (EPP)', 0, 25, 22,  'unit', None,      'Lentes Uvex, policarbonato, anti-rayadura'),
    # Consumibles
    ('Tapones Auditivos (caja)',   'Consumibles Obra',           0, 10,  8,  'box',  None,      'Caja 200 pares, NRR 33dB'),
    ('Tornillos Drywall 1" (caja)','Consumibles Obra',           1, 50, 42,  'box',  None,      'Caja 1000 pzas, fosfatados'),
    ('Cinta Masking 2" (rollo)',   'Consumibles Obra',           1, 30, 26,  'unit', None,      'Cinta masking Scotch, 50m'),
    ('Disco de Corte 4.5"',        'Consumibles Obra',           1, 60, 51,  'unit', None,      'Disco abrasivo Norton, metal'),
    ('Sellador Silicona (tubo)',   'Consumibles Obra',           1, 20, 16,  'unit', None,      'Silicona neutra GE, transparente'),
    # Material Electrico
    ('Cable THW 12 AWG (metro)',   'Material Electrico',         2,200,175,  'meter',None,      'Cable cobre THW negro, 600V'),
    ('Conector Rapido Wago 3p',    'Material Electrico',         2,100, 87,  'unit', None,      'Conector Wago 221-413, 3 entradas'),
    ('Breaker 20A 1P',             'Material Electrico',         2, 15, 11,  'unit', None,      'Interruptor termomagnetico Schneider'),
]

materials_list = []
for (nombre, cat_key, loc_idx, qty, avail, unidad, serie, desc) in materiales_data:
    loc = locations[loc_idx]
    cat = categories[cat_key]
    mat, created = Material.objects.get_or_create(
        account=account,
        name=nombre,
        defaults={
            'category': cat,
            'location': loc,
            'quantity': qty,
            'available_quantity': avail,
            'unit_of_measure': unidad,
            'serial_number': serie,
            'description': desc,
            'status': 'available',
            'is_available_for_loan': True,
            'min_stock_level': max(1, qty // 5),
        }
    )
    materials_list.append(mat)
    print("  + Material: " + nombre + " (qty=" + str(qty) + ")")

print("\nOK " + str(len(materials_list)) + " materiales creados")

# --- 8. SOLICITUDES (LoanRequests) ---
no_consumibles = [m for m in materials_list if not m.is_consumable]
consumibles    = [m for m in materials_list if m.is_consumable]
today = date.today()

def make_request(requester, items_spec, status, dias_pickup, dias_return, notas='', reviewer=None):
    pickup = today + timedelta(days=dias_pickup)
    ret    = today + timedelta(days=dias_return) if dias_return else None
    notes_map = {'approved': 'Aprobado', 'rejected': 'Rechazado: sin stock suficiente'}
    req = LoanRequest.objects.create(
        account=account,
        requester=requester,
        desired_pickup_date=pickup,
        desired_return_date=ret,
        status=status,
        purpose=notas,
        reviewed_by=reviewer,
        reviewed_at=timezone.now() if reviewer else None,
        review_notes=notes_map.get(status, ''),
    )
    for mat, qty in items_spec:
        LoanRequestItem.objects.create(loan_request=req, material=mat, quantity_requested=qty)
    return req

# Pendientes
req1 = make_request(
    ernesto,
    [(no_consumibles[0], 2), (no_consumibles[1], 1), (no_consumibles[4], 3)],
    'pending', 2, 10,
    'Proyecto fachada norte - herramientas para medicion y fijacion'
)
req2 = make_request(
    empleados[0],
    [(no_consumibles[5], 1), (no_consumibles[6], 1)],
    'pending', 1, 7,
    'Instalacion electrica bodega 3'
)
req3 = make_request(
    empleados[1],
    [(consumibles[0], 10), (consumibles[2], 20)],
    'pending', 3, None,
    'Consumibles para revestimiento de muros'
)

# Aprobadas (listas para entregar)
req4 = make_request(
    empleados[2],
    [(no_consumibles[3], 1), (no_consumibles[7], 1), (no_consumibles[8], 1)],
    'approved', 0, 5,
    'Mediciones planta baja',
    reviewer=inv
)
req5 = make_request(
    empleados[3],
    [(consumibles[1], 5), (consumibles[3], 2)],
    'approved', 0, None,
    'Material de trabajo diario',
    reviewer=inv
)

# Completadas (ya entregadas)
req6 = make_request(
    ernesto,
    [(no_consumibles[2], 1), (no_consumibles[9], 2)],
    'completed', -5, 3,
    'Demolicion area 4',
    reviewer=inv
)
req7 = make_request(
    empleados[4],
    [(no_consumibles[10], 4), (no_consumibles[11], 4)],
    'completed', -7, -1,
    'EPP semana de trabajo',
    reviewer=inv
)

# Rechazada
req8 = make_request(
    empleados[0],
    [(no_consumibles[5], 3)],
    'rejected', -3, 2,
    'Necesito taladros adicionales',
    reviewer=inv
)

print("\nOK 8 LoanRequests creados")

# --- 9. PRESTAMOS (Loans) ---
def make_loan(borrower, material, qty, dias_esperado, from_request=None, status='active', dias_atras=1):
    issued = timezone.now() - timedelta(days=dias_atras)
    exp_ret = today + timedelta(days=dias_esperado) if dias_esperado is not None else None
    loan = Loan.objects.create(
        account=account,
        borrower=borrower,
        material=material,
        quantity_loaned=qty,
        issued_by=inv,
        loan_request=from_request,
        expected_return_date=exp_ret,
        status=status,
        condition_on_pickup='good',
        issued_at=issued,
        is_consumable_loan=material.is_consumable,
    )
    return loan

# Activos
make_loan(ernesto,      no_consumibles[0],  2, 8,   req6, 'active', 5)
make_loan(ernesto,      no_consumibles[9],  2, 8,   req6, 'active', 5)
make_loan(empleados[2], no_consumibles[3],  1, 5,   req4, 'active', 1)
make_loan(empleados[2], no_consumibles[7],  1, 5,   req4, 'active', 1)
make_loan(empleados[2], no_consumibles[8],  1, 5,   req4, 'active', 1)

# Vencidos
loan_v1 = make_loan(empleados[1], no_consumibles[5], 1, -3, None, 'active', 10)
loan_v1.status = 'overdue'
loan_v1.save()
loan_v2 = make_loan(empleados[4], no_consumibles[6], 1, -5, None, 'active', 15)
loan_v2.status = 'overdue'
loan_v2.save()

# Consumibles activos
make_loan(empleados[3], consumibles[1], 5, None, req5, 'active', 1)
make_loan(empleados[3], consumibles[3], 2, None, req5, 'active', 1)

# Devueltos (historial)
loan_r1 = make_loan(ernesto,      no_consumibles[2], 1, 7, req6, 'active', 12)
loan_r1.status = 'returned'
loan_r1.actual_return_date = timezone.now() - timedelta(days=3)
loan_r1.condition_on_return = 'good'
loan_r1.save()

loan_r2 = make_loan(empleados[4], no_consumibles[10], 4, 5, req7, 'active', 8)
loan_r2.status = 'returned'
loan_r2.actual_return_date = timezone.now() - timedelta(days=2)
loan_r2.condition_on_return = 'good'
loan_r2.save()

loan_r3 = make_loan(empleados[4], no_consumibles[11], 4, 5, req7, 'active', 8)
loan_r3.status = 'returned'
loan_r3.actual_return_date = timezone.now() - timedelta(days=2)
loan_r3.condition_on_return = 'fair'
loan_r3.damage_notes = 'Leve desgaste en visera'
loan_r3.save()

print("\nOK Loans creados (activos, vencidos, devueltos)")

# --- RESUMEN ---
from accounts.models import Account, User
from materials.models import Material
from loans.models import LoanRequest, Loan

print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print("  Cuenta:         " + account.company_name + " (code=" + account.company_code + ")")
print("  Usuarios:       " + str(User.objects.filter(account=account).count()))
print("  Materiales:     " + str(Material.objects.filter(account=account).count()))
print("  Ubicaciones:    " + str(Location.objects.filter(account=account).count()))
print("  Categorias:     " + str(Category.objects.filter(account=account).count()))
print("  LoanRequests:   " + str(LoanRequest.objects.filter(account=account).count()))
print("    Pendientes:   " + str(LoanRequest.objects.filter(account=account, status='pending').count()))
print("    Aprobadas:    " + str(LoanRequest.objects.filter(account=account, status='approved').count()))
print("    Completadas:  " + str(LoanRequest.objects.filter(account=account, status='completed').count()))
print("    Rechazadas:   " + str(LoanRequest.objects.filter(account=account, status='rejected').count()))
print("  Loans:          " + str(Loan.objects.filter(account=account).count()))
print("    Activos:      " + str(Loan.objects.filter(account=account, status='active').count()))
print("    Vencidos:     " + str(Loan.objects.filter(account=account, status='overdue').count()))
print("    Devueltos:    " + str(Loan.objects.filter(account=account, status='returned').count()))
print()
print("CREDENCIALES:")
print("  Inventarista:  inventario@axisconstruccion.mx / axis2024")
print("  Movil (Ernesto): ernesto.garcia@axisconstruccion.mx / ernesto123")
print("  Empleados web: carlos/sofia/miguel/diana/roberto@axisconstruccion.mx / empleado123")
print("=" * 60)
print("Seed completado!")
