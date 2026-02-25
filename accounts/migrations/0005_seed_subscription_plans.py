from django.db import migrations


PLANS = [
    {
        'name': 'monthly',
        'display_name': 'Plan Mensual',
        'price': 5.00,
        'duration_days': 30,
        'max_users': -1,
        'max_locations': -1,
        'is_active': True,
    },
    {
        'name': 'quarterly',
        'display_name': 'Plan Trimestral',
        'price': 12.00,
        'duration_days': 90,
        'max_users': -1,
        'max_locations': -1,
        'is_active': True,
    },
    {
        'name': 'annual',
        'display_name': 'Plan Anual',
        'price': 50.00,
        'duration_days': 365,
        'max_users': -1,
        'max_locations': -1,
        'is_active': True,
    },
]


def seed_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('accounts', 'SubscriptionPlan')
    for plan_data in PLANS:
        SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data,
        )


def delete_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('accounts', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(
        name__in=[p['name'] for p in PLANS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_subscriptionplan_alter_account_subscription_plan_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_code=delete_plans),
    ]
