from rest_framework import serializers
from materials.models import Location


class LocationSerializer(serializers.ModelSerializer):
    full_address = serializers.ReadOnlyField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'account', 'name', 'description', 'street', 'exterior_number',
            'interior_number', 'neighborhood', 'postal_code', 'city', 'state',
            'country', 'is_active', 'full_address', 'is_locked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'account', 'full_address', 'is_locked', 'created_at', 'updated_at']

    def get_is_locked(self, obj):
        locked_ids = self.context.get('locked_ids', set())
        return obj.id in locked_ids
