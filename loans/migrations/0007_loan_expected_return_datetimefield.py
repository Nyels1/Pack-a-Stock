from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0006_loanrequest_datetime_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='expected_return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='loanextension',
            name='new_return_date',
            field=models.DateTimeField(),
        ),
    ]
