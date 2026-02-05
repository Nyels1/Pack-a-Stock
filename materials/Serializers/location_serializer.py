from rest_framework import serializers
from materials.models import Location


class LocationSerializer(serializers.ModelSerializer):
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'account', 'name', 'description', 'street', 'exterior_number',
            'interior_number', 'neighborhood', 'postal_code', 'city', 'state',
            'country', 'is_active', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'account', 'full_address', 'created_at', 'updated_at']
