from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_loan_request_return_date_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanrequest',
            name='desired_pickup_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='loanrequest',
            name='desired_return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
