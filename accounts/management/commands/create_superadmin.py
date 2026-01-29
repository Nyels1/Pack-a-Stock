from django.core.management.base import BaseCommand
from accounts.models import Account, User


class Command(BaseCommand):
    help = 'Crea un usuario superadmin con credenciales admin/12345'

    def handle(self, *args, **options):
        # Crear o obtener account por defecto
        account, created = Account.objects.get_or_create(
            email='admin@packstock.local',
            defaults={
                'company_name': 'Pack-a-Stock Admin',
                'country': 'México',
                'subscription_plan': 'premium',
                'max_locations': 999,
                'max_users': 999,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cuenta creada: {account.company_name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'! Cuenta existente: {account.company_name}')
            )

        # Crear o actualizar superadmin
        user, created = User.objects.get_or_create(
            email='admin',
            defaults={
                'full_name': 'Administrator',
                'account': account,
                'user_type': 'inventarista',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        # Establecer contraseña
        user.set_password('12345')
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Superadmin creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('! Superadmin actualizado')
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                'Credenciales del Superadmin:\n'
                '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                '📧 Email: admin\n'
                '🔑 Contraseña: 12345\n'
                '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            )
        )
