from django.db import migrations, models
import uuid


def generate_codes(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    for account in Account.objects.all():
        account.company_code = uuid.uuid4().hex[:8].upper()
        account.save(update_fields=['company_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_seed_subscription_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='company_code',
            field=models.CharField(
                blank=True, default='', max_length=12,
                help_text='Código de 8 caracteres para registro de empleados'
            ),
        ),
        migrations.RunPython(generate_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='account',
            name='company_code',
            field=models.CharField(
                blank=True, max_length=12, unique=True,
                help_text='Código de 8 caracteres para registro de empleados'
            ),
        ),
    ]
