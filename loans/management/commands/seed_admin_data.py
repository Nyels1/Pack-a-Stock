"""
Comando para poblar la cuenta de admin@packastock.com con datos realistas y abundantes.

Usage:
    python manage.py seed_admin_data
"""

import uuid
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from accounts.models import Account, User, SubscriptionPlan, Payment
from materials.models import Category, Location, Material
from loans.models import LoanRequest, LoanRequestItem, Loan, LoanExtension


class Command(BaseCommand):
    help = 'Poblar cuenta admin@packastock.com con datos abundantes para demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando poblacion de datos...'))

        # Buscar usuario admin
        try:
            admin_user = User.objects.get(email='admin@packastock.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontro admin@packastock.com'))
            return

        account = admin_user.account

        # Actualizar cuenta con info completa
        account.company_name = account.company_name or 'Pack-a-Stock Industrial'
        account.street = account.street or 'Av. Insurgentes Sur'
        account.exterior_number = account.exterior_number or '1602'
        account.neighborhood = account.neighborhood or 'Benito Juarez'
        account.postal_code = account.postal_code or '03900'
        account.city = account.city or 'Ciudad de Mexico'
        account.state = account.state or 'CDMX'
        account.country = account.country or 'Mexico'
        account.phone = account.phone or '(55) 5555-1234'
        account.subscription_plan = 'annual'
        account.max_users = -1
        account.max_locations = -1
        account.subscription_start_date = date.today() - timedelta(days=45)
        account.subscription_end_date = date.today() + timedelta(days=320)
        account.save()
        self.stdout.write(self.style.SUCCESS(f'Cuenta actualizada: {account.company_name} (Premium Annual)'))

        # Crear planes de suscripcion si no existen
        plans = self.create_plans()

        # Crear pagos simulados
        self.create_payments(account, plans)

        # Crear usuarios
        users = self.create_users(account, admin_user)

        # Crear categorias
        categories = self.create_categories(account)

        # Crear ubicaciones
        locations = self.create_locations(account)

        # Crear materiales
        materials = self.create_materials(account, categories, locations)

        # Crear solicitudes de prestamo
        loan_requests = self.create_loan_requests(account, users, materials, admin_user)

        # Crear prestamos
        loans = self.create_loans(account, users, materials, admin_user)

        # Crear extensiones
        self.create_extensions(account, users, loans, admin_user)

        self.stdout.write(self.style.SUCCESS('\nDatos creados exitosamente:'))
        self.stdout.write(f'  Usuarios: {len(users)}')
        self.stdout.write(f'  Categorias: {len(categories)}')
        self.stdout.write(f'  Ubicaciones: {len(locations)}')
        self.stdout.write(f'  Materiales: {len(materials)}')
        self.stdout.write(f'  Solicitudes: {len(loan_requests)}')
        self.stdout.write(f'  Prestamos: {len(loans)}')

    def create_plans(self):
        plans = []
        plans_data = [
            {'name': 'monthly', 'display_name': 'Plan Mensual', 'price': 5.00, 'duration_days': 30},
            {'name': 'quarterly', 'display_name': 'Plan Trimestral', 'price': 12.00, 'duration_days': 90},
            {'name': 'annual', 'display_name': 'Plan Anual', 'price': 50.00, 'duration_days': 365},
        ]
        for p in plans_data:
            plan, _ = SubscriptionPlan.objects.get_or_create(
                name=p['name'],
                defaults={
                    'display_name': p['display_name'],
                    'price': p['price'],
                    'duration_days': p['duration_days'],
                    'max_users': -1,
                    'max_locations': -1,
                    'is_active': True,
                }
            )
            plans.append(plan)
        self.stdout.write(self.style.SUCCESS('Planes de suscripcion creados'))
        return plans

    def create_payments(self, account, plans):
        if Payment.objects.filter(account=account).exists():
            self.stdout.write('Pagos ya existen, omitiendo...')
            return

        annual_plan = next(p for p in plans if p.name == 'annual')
        # Pago del plan anual
        Payment.objects.create(
            account=account,
            plan=annual_plan,
            amount=50.00,
            card_last_four='4532',
            card_holder_name='Admin Pack-a-Stock',
            status='completed',
        )
        # Pago anterior mensual
        monthly_plan = next(p for p in plans if p.name == 'monthly')
        p2 = Payment.objects.create(
            account=account,
            plan=monthly_plan,
            amount=5.00,
            card_last_four='4532',
            card_holder_name='Admin Pack-a-Stock',
            status='completed',
        )
        # Ajustar fecha del pago anterior
        Payment.objects.filter(pk=p2.pk).update(paid_at=timezone.now() - timedelta(days=60))
        self.stdout.write(self.style.SUCCESS('Pagos simulados creados'))

    def create_users(self, account, admin_user):
        users = [admin_user]
        users_data = [
            {'email': 'maria.gonzalez@packastock.com', 'full_name': 'Maria Gonzalez', 'user_type': 'inventarista'},
            {'email': 'roberto.silva@packastock.com', 'full_name': 'Roberto Silva', 'user_type': 'inventarista'},
            {'email': 'juan.perez@packastock.com', 'full_name': 'Juan Perez', 'user_type': 'employee'},
            {'email': 'ana.rodriguez@packastock.com', 'full_name': 'Ana Rodriguez', 'user_type': 'employee'},
            {'email': 'carlos.lopez@packastock.com', 'full_name': 'Carlos Lopez', 'user_type': 'employee'},
            {'email': 'laura.martinez@packastock.com', 'full_name': 'Laura Martinez', 'user_type': 'employee'},
            {'email': 'pedro.sanchez@packastock.com', 'full_name': 'Pedro Sanchez', 'user_type': 'employee'},
            {'email': 'sofia.ramirez@packastock.com', 'full_name': 'Sofia Ramirez', 'user_type': 'employee'},
            {'email': 'diego.torres@packastock.com', 'full_name': 'Diego Torres', 'user_type': 'employee'},
            {'email': 'lucia.flores@packastock.com', 'full_name': 'Lucia Flores', 'user_type': 'employee'},
        ]
        for u in users_data:
            user, created = User.objects.get_or_create(
                email=u['email'],
                defaults={
                    'account': account,
                    'full_name': u['full_name'],
                    'user_type': u['user_type'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('12345')
                user.save()
                self.stdout.write(f'  + {user.full_name} ({user.user_type})')
            users.append(user)

        # Bloquear un usuario de ejemplo
        blocked = next((u for u in users if u.email == 'diego.torres@packastock.com'), None)
        if blocked and not blocked.is_blocked:
            blocked.is_blocked = True
            blocked.blocked_reason = 'Prestamo vencido no devuelto - Material danado'
            blocked.blocked_until = timezone.now() + timedelta(days=14)
            blocked.save()
            self.stdout.write(self.style.WARNING(f'  ! {blocked.full_name} bloqueado'))

        self.stdout.write(self.style.SUCCESS(f'Usuarios creados/verificados: {len(users)}'))
        return users

    def create_categories(self, account):
        cats_data = [
            {'name': 'Electronica', 'is_consumable': False, 'description': 'Equipos electronicos y dispositivos'},
            {'name': 'Herramientas', 'is_consumable': False, 'description': 'Herramientas manuales y electricas'},
            {'name': 'Material de Oficina', 'is_consumable': True, 'description': 'Papeleria y materiales de oficina'},
            {'name': 'Equipos de Seguridad', 'is_consumable': False, 'description': 'EPP y equipos de proteccion'},
            {'name': 'Limpieza', 'is_consumable': True, 'description': 'Productos de limpieza e higiene'},
            {'name': 'Cables y Conectores', 'is_consumable': True, 'description': 'Cables, adaptadores y conectores'},
            {'name': 'Mobiliario', 'is_consumable': False, 'description': 'Muebles y mobiliario de oficina'},
            {'name': 'Vehiculos', 'is_consumable': False, 'description': 'Vehiculos y transporte'},
        ]
        categories = []
        for c in cats_data:
            cat, _ = Category.objects.get_or_create(
                account=account, name=c['name'],
                defaults={'is_consumable': c['is_consumable'], 'description': c.get('description', '')}
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'Categorias: {len(categories)}'))
        return categories

    def create_locations(self, account):
        locs_data = [
            {
                'name': 'Almacen Principal',
                'description': 'Almacen central de materiales',
                'street': 'Av. Insurgentes Sur', 'exterior_number': '1602',
                'neighborhood': 'Benito Juarez', 'postal_code': '03900',
                'city': 'Ciudad de Mexico', 'state': 'CDMX',
            },
            {
                'name': 'Bodega Norte',
                'description': 'Bodega de herramientas y equipos pesados',
                'street': 'Calle Reforma', 'exterior_number': '567',
                'neighborhood': 'Centro', 'postal_code': '06000',
                'city': 'Ciudad de Mexico', 'state': 'CDMX',
            },
            {
                'name': 'Oficina Central',
                'description': 'Oficinas administrativas',
                'street': 'Av. Revolucion', 'exterior_number': '890',
                'neighborhood': 'San Angel', 'postal_code': '01000',
                'city': 'Ciudad de Mexico', 'state': 'CDMX',
            },
            {
                'name': 'Taller Mecanico',
                'description': 'Area de mantenimiento y reparacion',
                'street': 'Blvd. Adolfo Lopez Mateos', 'exterior_number': '2100',
                'neighborhood': 'Tlalpan', 'postal_code': '14000',
                'city': 'Ciudad de Mexico', 'state': 'CDMX',
            },
        ]
        locations = []
        for loc in locs_data:
            l, _ = Location.objects.get_or_create(
                account=account, name=loc['name'],
                defaults=loc
            )
            locations.append(l)
        self.stdout.write(self.style.SUCCESS(f'Ubicaciones: {len(locations)}'))
        return locations

    def create_materials(self, account, categories, locations):
        cat_map = {c.name: c for c in categories}
        mats_data = [
            # Electronica
            {'name': 'Laptop Dell XPS 15', 'category': 'Electronica', 'location': 0, 'quantity': 8, 'min_stock': 3,
             'description': 'Dell XPS 15, i7, 16GB RAM, 512GB SSD'},
            {'name': 'Laptop HP ProBook 450', 'category': 'Electronica', 'location': 2, 'quantity': 5, 'min_stock': 2,
             'description': 'HP ProBook 450 G10, i5, 8GB RAM'},
            {'name': 'Proyector Epson', 'category': 'Electronica', 'location': 2, 'quantity': 4, 'min_stock': 1,
             'description': 'Proyector Epson Full HD 3000 lumens'},
            {'name': 'Monitor LG 27"', 'category': 'Electronica', 'location': 0, 'quantity': 12, 'min_stock': 4,
             'description': 'Monitor LG 27" 4K UHD IPS'},
            {'name': 'Tablet Samsung Galaxy Tab', 'category': 'Electronica', 'location': 0, 'quantity': 6, 'min_stock': 2,
             'description': 'Samsung Galaxy Tab S9, 128GB'},
            {'name': 'Camara Canon EOS', 'category': 'Electronica', 'location': 0, 'quantity': 3, 'min_stock': 1,
             'description': 'Canon EOS R50 con lente 18-45mm'},
            # Herramientas
            {'name': 'Taladro DeWalt', 'category': 'Herramientas', 'location': 1, 'quantity': 6, 'min_stock': 2,
             'description': 'Taladro inalambrico DeWalt 20V'},
            {'name': 'Sierra Circular', 'category': 'Herramientas', 'location': 1, 'quantity': 3, 'min_stock': 1,
             'description': 'Sierra circular profesional 7 1/4"'},
            {'name': 'Juego de Llaves', 'category': 'Herramientas', 'location': 3, 'quantity': 5, 'min_stock': 2,
             'description': 'Juego de llaves combinadas 8-22mm'},
            {'name': 'Multimetro Fluke', 'category': 'Herramientas', 'location': 3, 'quantity': 4, 'min_stock': 1,
             'description': 'Multimetro digital Fluke 117'},
            {'name': 'Compresor de Aire', 'category': 'Herramientas', 'location': 3, 'quantity': 2, 'min_stock': 1,
             'description': 'Compresor portatil 6 galones'},
            # Seguridad
            {'name': 'Casco de Seguridad', 'category': 'Equipos de Seguridad', 'location': 0, 'quantity': 20, 'min_stock': 8,
             'description': 'Casco industrial certificado ANSI'},
            {'name': 'Lentes de Seguridad', 'category': 'Equipos de Seguridad', 'location': 0, 'quantity': 25, 'min_stock': 10,
             'description': 'Lentes anti-impacto transparentes'},
            {'name': 'Chaleco Reflectante', 'category': 'Equipos de Seguridad', 'location': 0, 'quantity': 15, 'min_stock': 5,
             'description': 'Chaleco alta visibilidad clase 2'},
            {'name': 'Guantes de Seguridad', 'category': 'Equipos de Seguridad', 'location': 0, 'quantity': 30, 'min_stock': 10,
             'description': 'Guantes de trabajo resistentes al corte'},
            # Material de Oficina (consumible)
            {'name': 'Hojas de Papel Carta', 'category': 'Material de Oficina', 'location': 2, 'quantity': 50, 'min_stock': 10,
             'unit': 'box', 'description': 'Resma 500 hojas tamano carta'},
            {'name': 'Boligrafos BIC', 'category': 'Material de Oficina', 'location': 2, 'quantity': 30, 'min_stock': 8,
             'unit': 'box', 'description': 'Caja de 50 boligrafos azules'},
            {'name': 'Marcadores', 'category': 'Material de Oficina', 'location': 2, 'quantity': 25, 'min_stock': 8,
             'unit': 'package', 'description': 'Paquete de 12 marcadores colores'},
            {'name': 'Post-it Notas', 'category': 'Material de Oficina', 'location': 2, 'quantity': 40, 'min_stock': 10,
             'unit': 'package', 'description': 'Block de 100 notas adhesivas'},
            # Limpieza (consumible)
            {'name': 'Desinfectante', 'category': 'Limpieza', 'location': 1, 'quantity': 30, 'min_stock': 10,
             'unit': 'liter', 'description': 'Desinfectante multiusos 1L'},
            {'name': 'Toallas de Papel', 'category': 'Limpieza', 'location': 1, 'quantity': 45, 'min_stock': 15,
             'description': 'Rollo de toallas industrial'},
            {'name': 'Jabon Liquido', 'category': 'Limpieza', 'location': 1, 'quantity': 20, 'min_stock': 5,
             'unit': 'liter', 'description': 'Jabon liquido antibacterial 1L'},
            # Cables (consumible)
            {'name': 'Cable HDMI 2m', 'category': 'Cables y Conectores', 'location': 0, 'quantity': 40, 'min_stock': 10,
             'description': 'Cable HDMI 2.0 de 2 metros'},
            {'name': 'Cable USB-C', 'category': 'Cables y Conectores', 'location': 0, 'quantity': 50, 'min_stock': 15,
             'description': 'Cable USB-C a USB-A 1 metro'},
            {'name': 'Cable de Red Cat6', 'category': 'Cables y Conectores', 'location': 0, 'quantity': 35, 'min_stock': 10,
             'description': 'Cable Ethernet Cat6 3 metros'},
            {'name': 'Adaptador USB-C a HDMI', 'category': 'Cables y Conectores', 'location': 0, 'quantity': 15, 'min_stock': 5,
             'description': 'Adaptador USB-C a HDMI 4K'},
            # Mobiliario
            {'name': 'Silla Ergonomica', 'category': 'Mobiliario', 'location': 2, 'quantity': 10, 'min_stock': 3,
             'description': 'Silla ergonomica con soporte lumbar'},
            {'name': 'Escritorio Portatil', 'category': 'Mobiliario', 'location': 0, 'quantity': 5, 'min_stock': 1,
             'description': 'Mesa plegable para trabajo temporal'},
            # Vehiculos
            {'name': 'Camioneta Ford Ranger', 'category': 'Vehiculos', 'location': 3, 'quantity': 2, 'min_stock': 1,
             'description': 'Camioneta Ford Ranger 2024, placas ABC-1234'},
            {'name': 'Carretilla Electrica', 'category': 'Vehiculos', 'location': 1, 'quantity': 3, 'min_stock': 1,
             'description': 'Carretilla electrica para almacen'},
        ]

        materials = []
        for m in mats_data:
            cat = cat_map.get(m['category'])
            if not cat:
                continue
            loc = locations[m['location']] if m['location'] < len(locations) else locations[0]
            mat, created = Material.objects.get_or_create(
                account=account, name=m['name'],
                defaults={
                    'category': cat,
                    'location': loc,
                    'quantity': m['quantity'],
                    'available_quantity': m['quantity'],
                    'min_stock_level': m.get('min_stock', 0),
                    'unit_of_measure': m.get('unit', 'unit'),
                    'description': m.get('description', ''),
                    'status': 'available',
                    'is_available_for_loan': True,
                }
            )
            if created:
                self.stdout.write(f'  + {mat.name} (x{mat.quantity})')
            materials.append(mat)

        self.stdout.write(self.style.SUCCESS(f'Materiales: {len(materials)}'))
        return materials

    def create_loan_requests(self, account, users, materials, admin_user):
        employees = [u for u in users if u.user_type == 'employee']
        inventaristas = [u for u in users if u.user_type == 'inventarista']
        if not employees:
            return []

        mat_map = {m.name: m for m in materials}
        requests = []

        requests_data = [
            # Pendientes
            {
                'requester': 0, 'status': 'pending',
                'pickup': 2, 'return': 9,
                'purpose': 'Presentacion para cliente importante en Monterrey',
                'items': [('Laptop Dell XPS 15', 1), ('Proyector Epson', 1), ('Cable HDMI 2m', 2)],
            },
            {
                'requester': 1, 'status': 'pending',
                'pickup': 1, 'return': 5,
                'purpose': 'Reparaciones electricas en planta norte',
                'items': [('Taladro DeWalt', 1), ('Multimetro Fluke', 1), ('Casco de Seguridad', 2)],
            },
            {
                'requester': 3, 'status': 'pending',
                'pickup': 3, 'return': 10,
                'purpose': 'Inventario fisico del almacen bodega norte',
                'items': [('Tablet Samsung Galaxy Tab', 2)],
            },
            {
                'requester': 5, 'status': 'pending',
                'pickup': 0, 'return': 7,
                'purpose': 'Sesion fotografica para catalogo de productos',
                'items': [('Camara Canon EOS', 1), ('Monitor LG 27"', 1)],
            },
            # Aprobadas
            {
                'requester': 2, 'status': 'approved',
                'pickup': 0, 'return': 7,
                'purpose': 'Trabajo en oficina temporal sector sur',
                'items': [('Laptop HP ProBook 450', 1), ('Silla Ergonomica', 1)],
                'reviewed_by': 0, 'review_notes': 'Aprobado, material disponible',
            },
            {
                'requester': 4, 'status': 'approved',
                'pickup': -1, 'return': 6,
                'purpose': 'Mantenimiento preventivo vehicular',
                'items': [('Juego de Llaves', 1), ('Compresor de Aire', 1)],
                'reviewed_by': 1, 'review_notes': 'Aprobado para mantenimiento programado',
            },
            {
                'requester': 6, 'status': 'approved',
                'pickup': -2, 'return': 5,
                'purpose': 'Evento corporativo en auditorio',
                'items': [('Proyector Epson', 1), ('Cable HDMI 2m', 1)],
                'reviewed_by': 0, 'review_notes': 'Evento aprobado por direccion',
            },
            # Rechazadas
            {
                'requester': 0, 'status': 'rejected',
                'pickup': -5, 'return': -1,
                'purpose': 'Uso personal fin de semana',
                'items': [('Camara Canon EOS', 1)],
                'reviewed_by': 0, 'review_notes': 'No se autoriza uso personal de equipos',
            },
            {
                'requester': 3, 'status': 'rejected',
                'pickup': -3, 'return': 4,
                'purpose': 'Prestamo a empresa externa',
                'items': [('Laptop Dell XPS 15', 3)],
                'reviewed_by': 1, 'review_notes': 'No se permite prestamo a terceros. Politica interna.',
            },
            # Completadas
            {
                'requester': 1, 'status': 'completed',
                'pickup': -15, 'return': -8,
                'purpose': 'Capacitacion de personal nuevo',
                'items': [('Laptop Dell XPS 15', 2), ('Proyector Epson', 1)],
                'reviewed_by': 0, 'review_notes': 'Completado exitosamente',
            },
            {
                'requester': 5, 'status': 'completed',
                'pickup': -20, 'return': -13,
                'purpose': 'Instalacion de red en sucursal nueva',
                'items': [('Cable de Red Cat6', 10), ('Adaptador USB-C a HDMI', 3)],
                'reviewed_by': 0, 'review_notes': 'Materiales consumidos en instalacion',
            },
        ]

        for rd in requests_data:
            emp = employees[rd['requester'] % len(employees)]
            lr = LoanRequest.objects.create(
                account=account,
                requester=emp,
                desired_pickup_date=date.today() + timedelta(days=rd['pickup']),
                desired_return_date=date.today() + timedelta(days=rd['return']),
                purpose=rd['purpose'],
                status=rd['status'],
            )

            if rd['status'] in ('approved', 'rejected', 'completed'):
                reviewer = inventaristas[rd.get('reviewed_by', 0) % len(inventaristas)]
                lr.reviewed_by = reviewer
                lr.reviewed_at = timezone.now() - timedelta(days=abs(rd.get('pickup', 0)) + 1)
                lr.review_notes = rd.get('review_notes', '')
                lr.save()

            for item_name, qty in rd['items']:
                mat = mat_map.get(item_name)
                if mat:
                    LoanRequestItem.objects.create(
                        loan_request=lr,
                        material=mat,
                        quantity_requested=qty,
                    )

            requests.append(lr)
            self.stdout.write(f'  + Solicitud #{lr.id} ({lr.status}) - {emp.full_name}')

        self.stdout.write(self.style.SUCCESS(f'Solicitudes: {len(requests)}'))
        return requests

    def create_loans(self, account, users, materials, admin_user):
        employees = [u for u in users if u.user_type == 'employee']
        inventaristas = [u for u in users if u.user_type == 'inventarista']
        mat_map = {m.name: m for m in materials}
        loans = []

        loans_data = [
            # Activos - todo bien
            {'borrower': 0, 'material': 'Laptop Dell XPS 15', 'qty': 1, 'return_days': 5,
             'condition': 'excellent', 'status': 'active'},
            {'borrower': 1, 'material': 'Monitor LG 27"', 'qty': 2, 'return_days': 3,
             'condition': 'good', 'status': 'active'},
            {'borrower': 2, 'material': 'Tablet Samsung Galaxy Tab', 'qty': 1, 'return_days': 7,
             'condition': 'excellent', 'status': 'active'},
            {'borrower': 3, 'material': 'Silla Ergonomica', 'qty': 1, 'return_days': 14,
             'condition': 'good', 'status': 'active'},
            {'borrower': 5, 'material': 'Laptop HP ProBook 450', 'qty': 1, 'return_days': 10,
             'condition': 'good', 'status': 'active'},
            # Activos - por vencer
            {'borrower': 4, 'material': 'Proyector Epson', 'qty': 1, 'return_days': 1,
             'condition': 'good', 'status': 'active'},
            {'borrower': 0, 'material': 'Camara Canon EOS', 'qty': 1, 'return_days': 0,
             'condition': 'excellent', 'status': 'active'},
            # Vencidos
            {'borrower': 2, 'material': 'Taladro DeWalt', 'qty': 1, 'return_days': -3,
             'condition': 'good', 'status': 'overdue'},
            {'borrower': 6, 'material': 'Casco de Seguridad', 'qty': 3, 'return_days': -7,
             'condition': 'excellent', 'status': 'overdue'},
            {'borrower': 3, 'material': 'Juego de Llaves', 'qty': 1, 'return_days': -10,
             'condition': 'fair', 'status': 'overdue'},
            {'borrower': 7, 'material': 'Sierra Circular', 'qty': 1, 'return_days': -5,
             'condition': 'good', 'status': 'overdue'},
            # Devueltos
            {'borrower': 0, 'material': 'Monitor LG 27"', 'qty': 1, 'return_days': -2,
             'condition': 'excellent', 'status': 'returned', 'return_condition': 'good'},
            {'borrower': 1, 'material': 'Laptop Dell XPS 15', 'qty': 1, 'return_days': -5,
             'condition': 'good', 'status': 'returned', 'return_condition': 'good'},
            {'borrower': 4, 'material': 'Chaleco Reflectante', 'qty': 2, 'return_days': -8,
             'condition': 'excellent', 'status': 'returned', 'return_condition': 'fair'},
            {'borrower': 5, 'material': 'Camara Canon EOS', 'qty': 1, 'return_days': -12,
             'condition': 'excellent', 'status': 'returned', 'return_condition': 'excellent'},
            {'borrower': 2, 'material': 'Escritorio Portatil', 'qty': 1, 'return_days': -15,
             'condition': 'good', 'status': 'returned', 'return_condition': 'poor',
             'damage_notes': 'Superficie rayada y una pata floja'},
            {'borrower': 3, 'material': 'Compresor de Aire', 'qty': 1, 'return_days': -6,
             'condition': 'good', 'status': 'returned', 'return_condition': 'good'},
            # Perdido
            {'borrower': 6, 'material': 'Multimetro Fluke', 'qty': 1, 'return_days': -20,
             'condition': 'excellent', 'status': 'lost'},
            # Consumibles
            {'borrower': 1, 'material': 'Hojas de Papel Carta', 'qty': 3, 'return_days': 0,
             'condition': 'excellent', 'status': 'returned', 'consumable': True},
            {'borrower': 3, 'material': 'Cable HDMI 2m', 'qty': 2, 'return_days': 0,
             'condition': 'excellent', 'status': 'returned', 'consumable': True},
            {'borrower': 0, 'material': 'Cable USB-C', 'qty': 5, 'return_days': 0,
             'condition': 'excellent', 'status': 'returned', 'consumable': True},
            {'borrower': 5, 'material': 'Desinfectante', 'qty': 2, 'return_days': 0,
             'condition': 'excellent', 'status': 'returned', 'consumable': True},
            {'borrower': 2, 'material': 'Boligrafos BIC', 'qty': 1, 'return_days': 0,
             'condition': 'excellent', 'status': 'returned', 'consumable': True},
        ]

        for ld in loans_data:
            emp = employees[ld['borrower'] % len(employees)]
            mat = mat_map.get(ld['material'])
            if not mat:
                continue

            issuer = inventaristas[0] if inventaristas else admin_user
            loan_kwargs = {
                'account': account,
                'borrower': emp,
                'issued_by': issuer,
                'material': mat,
                'quantity_loaned': ld['qty'],
                'condition_on_pickup': ld['condition'],
                'status': ld['status'],
            }

            if ld.get('consumable'):
                loan_kwargs['is_consumable_loan'] = True
                loan_kwargs['quantity_returned'] = ld['qty']
            else:
                loan_kwargs['expected_return_date'] = date.today() + timedelta(days=ld['return_days'])

            if ld['status'] == 'returned':
                loan_kwargs['returned_to'] = issuer
                loan_kwargs['quantity_returned'] = ld['qty']
                loan_kwargs['actual_return_date'] = timezone.now() - timedelta(days=1)
                loan_kwargs['condition_on_return'] = ld.get('return_condition', 'good')
                if ld.get('damage_notes'):
                    loan_kwargs['damage_notes'] = ld['damage_notes']

            if ld['status'] == 'lost':
                loan_kwargs['damage_notes'] = 'Material reportado como perdido por el empleado'

            try:
                loan = Loan.objects.create(**loan_kwargs)
                loans.append(loan)
                self.stdout.write(f'  + Prestamo #{loan.id} ({loan.status}) - {emp.full_name} - {mat.name}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Error creando prestamo: {e}'))

        # Actualizar available_quantity de materiales con prestamos activos
        for mat in materials:
            active_loaned = Loan.objects.filter(
                material=mat, status__in=['active', 'overdue']
            ).values_list('quantity_loaned', flat=True)
            total_loaned = sum(active_loaned)
            mat.available_quantity = max(0, mat.quantity - total_loaned)
            mat.save(update_fields=['available_quantity'])

        self.stdout.write(self.style.SUCCESS(f'Prestamos: {len(loans)}'))
        return loans

    def create_extensions(self, account, users, loans, admin_user):
        employees = [u for u in users if u.user_type == 'employee']
        inventaristas = [u for u in users if u.user_type == 'inventarista']
        active_loans = [l for l in loans if l.status in ('active', 'overdue')]

        if len(active_loans) < 2:
            return

        # Extension pendiente
        LoanExtension.objects.create(
            account=account,
            loan=active_loans[0],
            requested_by=active_loans[0].borrower,
            new_return_date=date.today() + timedelta(days=15),
            reason='Necesito mas tiempo para terminar el proyecto de instalacion',
            status='pending',
        )

        # Extension aprobada
        if len(active_loans) > 1:
            ext = LoanExtension.objects.create(
                account=account,
                loan=active_loans[1],
                requested_by=active_loans[1].borrower,
                new_return_date=date.today() + timedelta(days=10),
                reason='Cliente pidio una semana adicional para revision',
                status='approved',
                reviewed_by=inventaristas[0] if inventaristas else admin_user,
                reviewed_at=timezone.now() - timedelta(hours=5),
                review_notes='Aprobado, extender 10 dias',
            )

        self.stdout.write(self.style.SUCCESS('Extensiones creadas'))
