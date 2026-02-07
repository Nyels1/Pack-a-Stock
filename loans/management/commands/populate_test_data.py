"""
Management command to populate database with test data for Pack-a-Stock

Usage:
    python manage.py populate_test_data

This will create:
- Users (employees and admins)
- Categories (consumable and non-consumable)
- Locations
- Materials
- Loan requests (pending, approved, rejected)
- Active loans
- Overdue loans
- Returned loans
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from accounts.models import Account, User
from materials.models import Category, Location, Material
from loans.models import LoanRequest, LoanRequestItem, Loan


class Command(BaseCommand):
    help = 'Populate database with test data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting data population...'))

        # Get or create test account
        account, created = Account.objects.get_or_create(
            company_name='Pack-a-Stock Demo',
            defaults={
                'email': 'demo@packastock.com',
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created account: {account.company_name}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Using existing account: {account.company_name}'))

        # Create users
        self.stdout.write(self.style.SUCCESS('\n👥 Creating users...'))
        users = self.create_users(account)

        # Create categories
        self.stdout.write(self.style.SUCCESS('\n📁 Creating categories...'))
        categories = self.create_categories(account)

        # Create locations
        self.stdout.write(self.style.SUCCESS('\n📍 Creating locations...'))
        locations = self.create_locations(account)

        # Create materials
        self.stdout.write(self.style.SUCCESS('\n📦 Creating materials...'))
        materials = self.create_materials(account, categories, locations)

        # Create loan requests
        self.stdout.write(self.style.SUCCESS('\n📋 Creating loan requests...'))
        loan_requests = self.create_loan_requests(account, users, materials)

        # Create loans
        self.stdout.write(self.style.SUCCESS('\n🔄 Creating loans...'))
        loans = self.create_loans(account, users, materials)

        self.stdout.write(self.style.SUCCESS('\n\n✨ Data population completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   - Users: {len(users)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Categories: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Locations: {len(locations)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Materials: {len(materials)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Loan Requests: {len(loan_requests)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Loans: {len(loans)}'))

    def create_users(self, account):
        """Create test users"""
        users_data = [
            {
                'email': 'admin@packastock.com',
                'password': '12345',
                'full_name': 'Admin Principal',
                'user_type': 'inventarista',
            },
            {
                'email': 'inventarista@packastock.com',
                'password': '12345',
                'full_name': 'María González',
                'user_type': 'inventarista',
            },
            {
                'email': 'empleado1@packastock.com',
                'password': '12345',
                'full_name': 'Juan Pérez',
                'user_type': 'empleado',
            },
            {
                'email': 'empleado2@packastock.com',
                'password': '12345',
                'full_name': 'Ana Rodríguez',
                'user_type': 'empleado',
            },
            {
                'email': 'empleado3@packastock.com',
                'password': '12345',
                'full_name': 'Carlos López',
                'user_type': 'empleado',
            },
            {
                'email': 'empleado4@packastock.com',
                'password': '12345',
                'full_name': 'Laura Martínez',
                'user_type': 'empleado',
            },
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'account': account,
                    'full_name': user_data['full_name'],
                    'user_type': user_data['user_type'],
                    'is_active': True,
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'  ✅ Created user: {user.full_name} ({user.user_type})')
            else:
                self.stdout.write(f'  ⚠️  Existing user: {user.full_name}')

            users.append(user)

        return users

    def create_categories(self, account):
        """Create test categories"""
        categories_data = [
            {'name': 'Electrónica', 'is_consumable': False},
            {'name': 'Herramientas', 'is_consumable': False},
            {'name': 'Material de Oficina', 'is_consumable': True},
            {'name': 'Equipos de Seguridad', 'is_consumable': False},
            {'name': 'Consumibles de Limpieza', 'is_consumable': True},
            {'name': 'Cables y Conectores', 'is_consumable': True},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                account=account,
                name=cat_data['name'],
                defaults={'is_consumable': cat_data['is_consumable']}
            )

            if created:
                tipo = 'Consumible' if category.is_consumable else 'Retornable'
                self.stdout.write(f'  ✅ Created category: {category.name} ({tipo})')
            else:
                self.stdout.write(f'  ⚠️  Existing category: {category.name}')

            categories.append(category)

        return categories

    def create_locations(self, account):
        """Create test locations"""
        locations_data = [
            {
                'name': 'Almacén Principal',
                'street': 'Av. Insurgentes',
                'exterior_number': '1234',
                'neighborhood': 'Roma Norte',
                'postal_code': '06700',
                'city': 'Ciudad de México',
                'state': 'CDMX',
                'country': 'México',
            },
            {
                'name': 'Bodega Secundaria',
                'street': 'Calle Reforma',
                'exterior_number': '567',
                'neighborhood': 'Centro',
                'postal_code': '06000',
                'city': 'Ciudad de México',
                'state': 'CDMX',
                'country': 'México',
            },
            {
                'name': 'Oficina Central',
                'street': 'Av. Revolución',
                'exterior_number': '890',
                'neighborhood': 'San Ángel',
                'postal_code': '01000',
                'city': 'Ciudad de México',
                'state': 'CDMX',
                'country': 'México',
            },
        ]

        locations = []
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                account=account,
                name=loc_data['name'],
                defaults=loc_data
            )

            if created:
                self.stdout.write(f'  ✅ Created location: {location.name}')
            else:
                self.stdout.write(f'  ⚠️  Existing location: {location.name}')

            locations.append(location)

        return locations

    def create_materials(self, account, categories, locations):
        """Create test materials"""

        # Get categories by type
        electronics = next(c for c in categories if c.name == 'Electrónica')
        tools = next(c for c in categories if c.name == 'Herramientas')
        office = next(c for c in categories if c.name == 'Material de Oficina')
        safety = next(c for c in categories if c.name == 'Equipos de Seguridad')
        cleaning = next(c for c in categories if c.name == 'Consumibles de Limpieza')
        cables = next(c for c in categories if c.name == 'Cables y Conectores')

        materials_data = [
            # Non-consumable materials
            {
                'name': 'Laptop Dell XPS 15',
                'description': 'Laptop Dell XPS 15, Intel Core i7, 16GB RAM, 512GB SSD',
                'category': electronics,
                'location': locations[0],
                'quantity': 5,
                'min_stock_level': 2,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Proyector Epson',
                'description': 'Proyector Epson, Full HD 1080p, 3000 lumens',
                'category': electronics,
                'location': locations[2],
                'quantity': 3,
                'min_stock_level': 1,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Taladro Inalámbrico DeWalt',
                'description': 'Taladro inalámbrico DeWalt 20V con batería',
                'category': tools,
                'location': locations[1],
                'quantity': 4,
                'min_stock_level': 1,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Sierra Circular',
                'description': 'Sierra circular profesional 7 1/4"',
                'category': tools,
                'location': locations[1],
                'quantity': 2,
                'min_stock_level': 1,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Casco de Seguridad',
                'description': 'Casco de seguridad industrial certificado',
                'category': safety,
                'location': locations[0],
                'quantity': 10,
                'min_stock_level': 5,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Lentes de Seguridad',
                'description': 'Lentes de seguridad anti-impacto',
                'category': safety,
                'location': locations[0],
                'quantity': 15,
                'min_stock_level': 8,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            # Consumable materials
            {
                'name': 'Hojas de Papel Carta',
                'description': 'Resma de 500 hojas tamaño carta',
                'category': office,
                'location': locations[2],
                'quantity': 50,
                'min_stock_level': 10,
                'unit_of_measure': 'box',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Bolígrafos',
                'description': 'Caja de 50 bolígrafos azules',
                'category': office,
                'location': locations[2],
                'quantity': 20,
                'min_stock_level': 5,
                'unit_of_measure': 'box',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Marcadores',
                'description': 'Paquete de 12 marcadores de colores',
                'category': office,
                'location': locations[2],
                'quantity': 30,
                'min_stock_level': 10,
                'unit_of_measure': 'package',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Desinfectante',
                'description': 'Desinfectante multiusos 1L',
                'category': cleaning,
                'location': locations[1],
                'quantity': 25,
                'min_stock_level': 8,
                'unit_of_measure': 'liter',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Toallas de Papel',
                'description': 'Rollo de toallas de papel industrial',
                'category': cleaning,
                'location': locations[1],
                'quantity': 40,
                'min_stock_level': 15,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Cable HDMI',
                'description': 'Cable HDMI 2.0, 2 metros',
                'category': cables,
                'location': locations[0],
                'quantity': 35,
                'min_stock_level': 10,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
            {
                'name': 'Cable USB-C',
                'description': 'Cable USB-C a USB-A, 1 metro',
                'category': cables,
                'location': locations[0],
                'quantity': 45,
                'min_stock_level': 15,
                'unit_of_measure': 'unit',
                'status': 'available',
                'is_available_for_loan': True,
            },
        ]

        materials = []
        for mat_data in materials_data:
            material, created = Material.objects.get_or_create(
                account=account,
                name=mat_data['name'],
                defaults=mat_data
            )

            if created:
                # Fix available_quantity to match quantity
                material.available_quantity = material.quantity
                material.save(update_fields=['available_quantity'])
                tipo = 'Consumible' if material.is_consumable else 'Retornable'
                self.stdout.write(f'  ✅ Created material: {material.name} ({tipo})')
            else:
                self.stdout.write(f'  ⚠️  Existing material: {material.name}')

            materials.append(material)

        return materials

    def create_loan_requests(self, account, users, materials):
        """Create test loan requests"""

        # Get users by type
        admin = next(u for u in users if u.email == 'admin@packastock.com')
        inventarista = next(u for u in users if u.email == 'inventarista@packastock.com')
        empleado1 = next(u for u in users if u.email == 'empleado1@packastock.com')
        empleado2 = next(u for u in users if u.email == 'empleado2@packastock.com')
        empleado3 = next(u for u in users if u.email == 'empleado3@packastock.com')

        loan_requests = []

        # 1. Pending request (empleado1)
        lr1 = LoanRequest.objects.create(
            account=account,
            requester=empleado1,
            desired_pickup_date=date.today() + timedelta(days=2),
            desired_return_date=date.today() + timedelta(days=9),
            purpose='Presentación para cliente importante',
            status='pending',
        )
        LoanRequestItem.objects.create(
            loan_request=lr1,
            material=next(m for m in materials if m.name == 'Laptop Dell XPS 15'),
            quantity_requested=1,
        )
        LoanRequestItem.objects.create(
            loan_request=lr1,
            material=next(m for m in materials if m.name == 'Proyector Epson'),
            quantity_requested=1,
        )
        loan_requests.append(lr1)
        self.stdout.write(f'  ✅ Created pending request: {lr1}')

        # 2. Pending request (empleado2)
        lr2 = LoanRequest.objects.create(
            account=account,
            requester=empleado2,
            desired_pickup_date=date.today() + timedelta(days=1),
            desired_return_date=date.today() + timedelta(days=4),
            purpose='Trabajo de construcción en sitio',
            status='pending',
        )
        LoanRequestItem.objects.create(
            loan_request=lr2,
            material=next(m for m in materials if m.name == 'Taladro Inalámbrico DeWalt'),
            quantity_requested=1,
        )
        LoanRequestItem.objects.create(
            loan_request=lr2,
            material=next(m for m in materials if m.name == 'Casco de Seguridad'),
            quantity_requested=2,
        )
        loan_requests.append(lr2)
        self.stdout.write(f'  ✅ Created pending request: {lr2}')

        # 3. Approved request (empleado3)
        lr3 = LoanRequest.objects.create(
            account=account,
            requester=empleado3,
            desired_pickup_date=date.today(),
            desired_return_date=date.today() + timedelta(days=7),
            purpose='Reparaciones en oficina',
            status='approved',
            reviewed_by=admin,
            reviewed_at=timezone.now() - timedelta(hours=2),
            review_notes='Aprobado para reparaciones urgentes',
        )
        LoanRequestItem.objects.create(
            loan_request=lr3,
            material=next(m for m in materials if m.name == 'Sierra Circular'),
            quantity_requested=1,
        )
        loan_requests.append(lr3)
        self.stdout.write(f'  ✅ Created approved request: {lr3}')

        # 4. Rejected request (empleado1)
        lr4 = LoanRequest.objects.create(
            account=account,
            requester=empleado1,
            desired_pickup_date=date.today() - timedelta(days=3),
            desired_return_date=date.today() + timedelta(days=4),
            purpose='Uso personal no autorizado',
            status='rejected',
            reviewed_by=inventarista,
            reviewed_at=timezone.now() - timedelta(days=2),
            review_notes='No se puede aprobar para uso personal',
        )
        LoanRequestItem.objects.create(
            loan_request=lr4,
            material=next(m for m in materials if m.name == 'Laptop Dell XPS 15'),
            quantity_requested=2,
        )
        loan_requests.append(lr4)
        self.stdout.write(f'  ✅ Created rejected request: {lr4}')

        return loan_requests

    def create_loans(self, account, users, materials):
        """Create test loans (active, overdue, returned)"""

        # Get users
        admin = next(u for u in users if u.email == 'admin@packastock.com')
        empleado1 = next(u for u in users if u.email == 'empleado1@packastock.com')
        empleado2 = next(u for u in users if u.email == 'empleado2@packastock.com')
        empleado3 = next(u for u in users if u.email == 'empleado3@packastock.com')
        empleado4 = next(u for u in users if u.email == 'empleado4@packastock.com')

        loans = []

        # 1. Active loan (within due date)
        loan1 = Loan.objects.create(
            account=account,
            borrower=empleado1,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Laptop Dell XPS 15'),
            quantity_loaned=1,
            expected_return_date=date.today() + timedelta(days=5),
            condition_on_pickup='excellent',
            status='active',
        )
        loans.append(loan1)
        self.stdout.write(f'  ✅ Created active loan: {loan1}')

        # 2. Active loan (due soon)
        loan2 = Loan.objects.create(
            account=account,
            borrower=empleado2,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Proyector Epson'),
            quantity_loaned=1,
            expected_return_date=date.today() + timedelta(days=1),
            condition_on_pickup='good',
            status='active',
        )
        loans.append(loan2)
        self.stdout.write(f'  ✅ Created active loan (due soon): {loan2}')

        # 3. Overdue loan
        loan3 = Loan.objects.create(
            account=account,
            borrower=empleado3,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Taladro Inalámbrico DeWalt'),
            quantity_loaned=1,
            expected_return_date=date.today() - timedelta(days=3),
            condition_on_pickup='good',
            status='overdue',
        )
        loans.append(loan3)
        self.stdout.write(f'  ✅ Created overdue loan: {loan3}')

        # 4. Overdue loan (very late)
        loan4 = Loan.objects.create(
            account=account,
            borrower=empleado4,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Casco de Seguridad'),
            quantity_loaned=2,
            expected_return_date=date.today() - timedelta(days=10),
            condition_on_pickup='excellent',
            status='overdue',
        )
        loans.append(loan4)
        self.stdout.write(f'  ✅ Created overdue loan (very late): {loan4}')

        # 5. Returned loan (good condition)
        loan5 = Loan.objects.create(
            account=account,
            borrower=empleado1,
            issued_by=admin,
            returned_to=admin,
            material=next(m for m in materials if m.name == 'Sierra Circular'),
            quantity_loaned=1,
            quantity_returned=1,
            expected_return_date=date.today() - timedelta(days=2),
            actual_return_date=timezone.now() - timedelta(days=1),
            condition_on_pickup='good',
            condition_on_return='good',
            status='returned',
        )
        loans.append(loan5)
        self.stdout.write(f'  ✅ Created returned loan: {loan5}')

        # 6. Consumable loan (auto-completed)
        loan6 = Loan.objects.create(
            account=account,
            borrower=empleado2,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Hojas de Papel Carta'),
            quantity_loaned=2,
            condition_on_pickup='excellent',
            # Status will be auto-set to 'returned' because it's consumable
        )
        loans.append(loan6)
        self.stdout.write(f'  ✅ Created consumable loan: {loan6}')

        # 7. Another consumable loan
        loan7 = Loan.objects.create(
            account=account,
            borrower=empleado3,
            issued_by=admin,
            material=next(m for m in materials if m.name == 'Cable HDMI'),
            quantity_loaned=2,
            condition_on_pickup='excellent',
        )
        loans.append(loan7)
        self.stdout.write(f'  ✅ Created consumable loan: {loan7}')

        return loans
