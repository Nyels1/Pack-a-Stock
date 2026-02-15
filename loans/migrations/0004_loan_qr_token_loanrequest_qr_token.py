import uuid
from django.db import migrations, models


def gen_uuid_loan(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    for row in Loan.objects.all():
        row.qr_token = uuid.uuid4()
        row.save(update_fields=['qr_token'])


def gen_uuid_loanrequest(apps, schema_editor):
    LoanRequest = apps.get_model('loans', 'LoanRequest')
    for row in LoanRequest.objects.all():
        row.qr_token = uuid.uuid4()
        row.save(update_fields=['qr_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0003_loanextension_account'),
    ]

    operations = [
        # Step 1: Add fields without unique constraint
        migrations.AddField(
            model_name='loan',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='loanrequest',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        # Step 2: Generate unique UUIDs for existing rows
        migrations.RunPython(gen_uuid_loan, migrations.RunPython.noop),
        migrations.RunPython(gen_uuid_loanrequest, migrations.RunPython.noop),
        # Step 3: Add unique constraint
        migrations.AlterField(
            model_name='loan',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='loanrequest',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
