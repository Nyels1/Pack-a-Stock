from rest_framework import serializers
from loans.models import Loan
from accounts.Serializers.user_serializer import UserSerializer
from materials.Serializers.material_serializer import MaterialMinimalSerializer


class LoanSerializer(serializers.ModelSerializer):
    borrower_detail = UserSerializer(source='borrower', read_only=True)
    issued_by_detail = UserSerializer(source='issued_by', read_only=True)
    returned_to_detail = UserSerializer(source='returned_to', read_only=True)
    material_detail = MaterialMinimalSerializer(source='material', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_return = serializers.ReadOnlyField()
    is_fully_returned = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'account', 'loan_request', 'borrower', 'borrower_detail',
            'issued_by', 'issued_by_detail', 'returned_to', 'returned_to_detail',
            'material', 'material_detail', 'quantity_loaned', 'quantity_returned',
            'is_consumable_loan', 'issued_at', 'expected_return_date',
            'actual_return_date', 'facial_auth_verified', 'facial_auth_at',
            'pickup_signature', 'return_signature', 'condition_on_pickup',
            'condition_on_return', 'damage_notes', 'status', 'is_overdue',
            'days_until_return', 'is_fully_returned', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'issued_at', 'actual_return_date', 'facial_auth_at',
            'is_overdue', 'days_until_return', 'is_fully_returned',
            'created_at', 'updated_at', 'is_consumable_loan'
        ]


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            'loan_request', 'borrower', 'material', 'quantity_loaned',
            'expected_return_date', 'pickup_signature', 'condition_on_pickup'
        ]


class LoanReturnSerializer(serializers.Serializer):
    condition_on_return = serializers.ChoiceField(
        choices=['excellent', 'good', 'fair', 'poor', 'damaged']
    )
    damage_notes = serializers.CharField(required=False, allow_blank=True)
    return_signature = serializers.CharField(required=False, allow_blank=True)
