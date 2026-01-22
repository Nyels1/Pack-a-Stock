from rest_framework import serializers
from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'company_name', 'street', 'exterior_number', 'interior_number',
            'neighborhood', 'postal_code', 'city', 'state', 'country', 'phone',
            'email', 'subscription_plan', 'max_locations', 'max_users', 'is_active',
            'subscription_start_date', 'subscription_end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'max_locations', 'max_users']
