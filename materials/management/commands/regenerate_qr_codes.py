from django.core.management.base import BaseCommand
from materials.models import Material
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode


class Command(BaseCommand):
    help = 'Regenera los códigos QR para materiales que no tienen imagen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar QR para TODOS los materiales',
        )

    def handle(self, *args, **options):
        if options['all']:
            materials = Material.objects.all()
            self.stdout.write(self.style.WARNING('Regenerando QR para TODOS los materiales...'))
        else:
            materials = Material.objects.filter(qr_image__isnull=True) | Material.objects.filter(qr_image='')
            self.stdout.write(self.style.WARNING(f'Regenerando QR para {materials.count()} materiales sin imagen...'))

        count = 0
        errors = 0

        for material in materials:
            try:
                if material.qr_code:
                    # Generar imagen QR
                    qr = qrcode.QRCode(box_size=8, border=2)
                    qr.add_data(material.qr_code)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    file_name = f"{material.qr_code}.png"
                    
                    # Limpiar imagen anterior si existe
                    if material.qr_image:
                        material.qr_image.delete(save=False)
                    
                    material.qr_image.save(file_name, ContentFile(buffer.read()), save=True)
                    buffer.close()
                    
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ QR generado para: {material.name} ({material.qr_code})'))
                    if material.qr_image:
                        self.stdout.write(f'  URL: {material.qr_image.url}')
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Material sin qr_code: {material.name}'))
                    errors += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error con {material.name}: {str(e)}'))
                errors += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ Proceso completado: {count} QR generados, {errors} errores'))
