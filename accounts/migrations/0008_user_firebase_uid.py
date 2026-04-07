from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_user_face_enrolled_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='firebase_uid',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
    ]
