"""
Parte 2 del seed Axis: limpia requests mal formados y crea requests + loans correctos.
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pack_a_stock_api.settings')
django.setup()

from datetime import date, timedelta
from django.utils import timezone
from accounts.models import Account, User
from materials.models import Material
from loans.models import LoanRequest, LoanRequestItem, Loan

acc = Account.objects.get(company_name='Axis')
inv = User.objects.get(email='inventario@axisconstruccion.mx')
ernesto = User.objects.get(email='ernesto.garcia@axisconstruccion.mx')
emp = list(User.objects.filter(account=acc, user_type='employee').exclude(email='ernesto.garcia@axisconstruccion.mx'))

# Limpiar todo lo anterior para empezar limpio
Loan.objects.filter(account=acc).delete()
LoanRequest.objects.filter(account=acc).delete()
print("OK Limpieza de requests y loans previa")

# Cargar materiales en orden de creacion
mats = list(Material.objects.filter(account=acc).order_by('id'))
no_cons = [m for m in mats if not m.is_consumable]
cons    = [m for m in mats if m.is_consumable]

print("No consumibles (" + str(len(no_cons)) + "):")
for i, m in enumerate(no_cons):
    print("  [" + str(i) + "] " + m.name + " avail=" + str(m.available_quantity))
print("Consumibles (" + str(len(cons)) + "):")
for i, m in enumerate(cons):
    print("  [" + str(i) + "] " + m.name + " avail=" + str(m.available_quantity))

today = date.today()

def make_request(requester, items_spec, status, dias_pickup, dias_return, notas='', reviewer=None):
    pickup = today + timedelta(days=dias_pickup)
    ret    = today + timedelta(days=dias_return) if dias_return else None
    notes_map = {'approved': 'Aprobado', 'rejected': 'Rechazado: sin stock suficiente'}
    req = LoanRequest.objects.create(
        account=acc,
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

def make_loan(borrower, material, qty, dias_esperado, from_request=None, status='active', dias_atras=1):
    exp_ret = today + timedelta(days=dias_esperado) if dias_esperado is not None else None
    loan = Loan.objects.create(
        account=acc,
        borrower=borrower,
        material=material,
        quantity_loaned=qty,
        issued_by=inv,
        loan_request=from_request,
        expected_return_date=exp_ret,
        status=status,
        condition_on_pickup='good',
        issued_at=timezone.now() - timedelta(days=dias_atras),
        is_consumable_loan=material.is_consumable,
    )
    return loan

# --- SOLICITUDES PENDIENTES ---
req1 = make_request(
    ernesto,
    [(no_cons[0], 2), (no_cons[1], 1), (no_cons[4], 3)],
    'pending', 2, 10,
    'Proyecto fachada norte - herramientas para medicion y fijacion'
)
print("OK req1 pendiente (Ernesto - herramientas)")

req2 = make_request(
    emp[0],
    [(no_cons[5], 1), (no_cons[6], 1)],
    'pending', 1, 7,
    'Instalacion electrica bodega 3'
)
print("OK req2 pendiente (Carlos - electricas)")

req3 = make_request(
    emp[1],
    [(cons[0], 5), (cons[2], 15)],
    'pending', 3, None,
    'Consumibles para revestimiento de muros'
)
print("OK req3 pendiente (Sofia - consumibles)")

# --- SOLICITUDES APROBADAS ---
req4 = make_request(
    emp[2],
    [(no_cons[3], 1), (no_cons[7], 1), (no_cons[8], 1)],
    'approved', 0, 5,
    'Mediciones planta baja',
    reviewer=inv
)
print("OK req4 aprobada (Miguel - medicion)")

req5 = make_request(
    emp[3],
    [(cons[1], 5), (cons[3], 2)],
    'approved', 0, None,
    'Material de trabajo diario',
    reviewer=inv
)
print("OK req5 aprobada (Diana - consumibles)")

# --- SOLICITUDES COMPLETADAS ---
req6 = make_request(
    ernesto,
    [(no_cons[2], 1), (no_cons[9], 2)],
    'completed', -5, 3,
    'Demolicion area 4',
    reviewer=inv
)
print("OK req6 completada (Ernesto - herramientas)")

req7 = make_request(
    emp[4],
    [(no_cons[10], 4), (no_cons[11], 4)],
    'completed', -7, -1,
    'EPP semana de trabajo',
    reviewer=inv
)
print("OK req7 completada (Roberto - EPP)")

# --- SOLICITUD RECHAZADA ---
req8 = make_request(
    emp[0],
    [(no_cons[5], 2)],
    'rejected', -3, 2,
    'Necesito taladros adicionales - urgente',
    reviewer=inv
)
print("OK req8 rechazada (Carlos)")

# --- PRESTAMOS ACTIVOS ---
make_loan(ernesto,  no_cons[0], 2, 8,   req6, 'active', 5)
make_loan(ernesto,  no_cons[9], 2, 8,   req6, 'active', 5)
make_loan(emp[2],   no_cons[3], 1, 5,   req4, 'active', 1)
make_loan(emp[2],   no_cons[7], 1, 5,   req4, 'active', 1)
make_loan(emp[2],   no_cons[8], 1, 5,   req4, 'active', 1)
print("OK 5 loans activos creados")

# --- VENCIDOS ---
l1 = make_loan(emp[1], no_cons[5], 1, -3, None, 'active', 10)
l1.status = 'overdue'; l1.save()
l2 = make_loan(emp[4], no_cons[6], 1, -5, None, 'active', 15)
l2.status = 'overdue'; l2.save()
print("OK 2 loans vencidos")

# --- CONSUMIBLES (no se devuelven) ---
make_loan(emp[3], cons[1], 5, None, req5, 'active', 1)
make_loan(emp[3], cons[3], 2, None, req5, 'active', 1)
print("OK 2 loans consumibles activos")

# --- DEVUELTOS (historial) ---
lr1 = make_loan(ernesto, no_cons[2], 1, 7, req6, 'active', 12)
lr1.status = 'returned'; lr1.actual_return_date = timezone.now() - timedelta(days=3)
lr1.condition_on_return = 'good'; lr1.save()

lr2 = make_loan(emp[4], no_cons[10], 4, 5, req7, 'active', 8)
lr2.status = 'returned'; lr2.actual_return_date = timezone.now() - timedelta(days=2)
lr2.condition_on_return = 'good'; lr2.save()

lr3 = make_loan(emp[4], no_cons[11], 4, 5, req7, 'active', 8)
lr3.status = 'returned'; lr3.actual_return_date = timezone.now() - timedelta(days=2)
lr3.condition_on_return = 'fair'; lr3.damage_notes = 'Leve desgaste en visera'; lr3.save()
print("OK 3 loans devueltos (historial)")

# --- RESUMEN ---
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print("  Cuenta:       " + acc.company_name + " (code=" + acc.company_code + ")")
print("  Usuarios:     " + str(User.objects.filter(account=acc).count()))
print("  Materiales:   " + str(Material.objects.filter(account=acc).count()))
print("  LoanRequests: " + str(LoanRequest.objects.filter(account=acc).count()))
print("    Pendientes: " + str(LoanRequest.objects.filter(account=acc, status='pending').count()))
print("    Aprobadas:  " + str(LoanRequest.objects.filter(account=acc, status='approved').count()))
print("    Completadas:" + str(LoanRequest.objects.filter(account=acc, status='completed').count()))
print("    Rechazadas: " + str(LoanRequest.objects.filter(account=acc, status='rejected').count()))
print("  Loans:        " + str(Loan.objects.filter(account=acc).count()))
print("    Activos:    " + str(Loan.objects.filter(account=acc, status='active').count()))
print("    Vencidos:   " + str(Loan.objects.filter(account=acc, status='overdue').count()))
print("    Devueltos:  " + str(Loan.objects.filter(account=acc, status='returned').count()))
print()
print("CREDENCIALES:")
print("  Web inventarista: inventario@axisconstruccion.mx / axis2024")
print("  Movil (Ernesto):  ernesto.garcia@axisconstruccion.mx / ernesto123")
print("  Empleados web:    carlos/sofia/miguel/diana/roberto@axisconstruccion.mx / empleado123")
print("=" * 60)
