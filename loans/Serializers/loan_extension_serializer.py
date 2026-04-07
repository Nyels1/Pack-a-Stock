from rest_framework import serializers
from loans.models import LoanExtension
from accounts.Serializers.user_serializer import UserSerializer


class LoanExtensionSerializer(serializers.ModelSerializer):
    requested_by_detail = UserSerializer(source='requested_by', read_only=True)
    reviewed_by_detail = UserSerializer(source='reviewed_by', read_only=True)
    material_name = serializers.SerializerMethodField()

    def get_material_name(self, obj):
        try:
            return obj.loan.material.name
        except Exception:
            return None

    class Meta:
        model = LoanExtension
        fields = [
            'id', 'loan', 'material_name', 'requested_by', 'requested_by_detail', 'requested_at',
            'new_return_date', 'reason', 'status', 'reviewed_by',
            'reviewed_by_detail', 'reviewed_at', 'review_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_at', 'reviewed_by', 'reviewed_at',
            'created_at', 'updated_at'
        ]


class LoanExtensionCreateSerializer(serializers.ModelSerializer):
    new_return_date = serializers.DateTimeField()

    class Meta:
        model = LoanExtension
        fields = ['loan', 'new_return_date', 'reason']
