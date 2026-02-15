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
            'id', 'account', 'qr_token', 'loan_request', 'borrower', 'borrower_detail',
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

    def validate_borrower(self, value):
        """Verificar si el usuario está bloqueado"""
        from django.utils import timezone

        if value.is_blocked:
            if value.blocked_until and value.blocked_until < timezone.now():
                # Desbloquear automáticamente si ya pasó la fecha
                value.is_blocked = False
                value.blocked_reason = None
                value.blocked_until = None
                value.save()
            else:
                blocked_msg = f"Usuario bloqueado"
                if value.blocked_until:
                    blocked_msg += f" hasta {value.blocked_until.strftime('%d/%m/%Y')}"
                if value.blocked_reason:
                    blocked_msg += f". Motivo: {value.blocked_reason}"
                raise serializers.ValidationError(blocked_msg)

        return value

    def validate_expected_return_date(self, value):
        """La fecha de devolución no puede ser anterior a hoy"""
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de devolución no puede ser anterior a hoy"
            )
        return value

    def validate(self, attrs):
        """Validar disponibilidad del material"""
        material = attrs.get('material')
        quantity = attrs.get('quantity_loaned', 1)

        if material:
            if material.available_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity_loaned': (
                        f"Stock insuficiente para '{material.name}'. "
                        f"Disponible: {material.available_quantity}, Solicitado: {quantity}"
                    )
                })

            if material.available_quantity <= 0:
                raise serializers.ValidationError({
                    'material': f"'{material.name}' no tiene unidades disponibles para préstamo"
                })

        return attrs


class LoanReturnSerializer(serializers.Serializer):
    condition_on_return = serializers.ChoiceField(
        choices=['excellent', 'good', 'fair', 'poor', 'damaged']
    )
    damage_notes = serializers.CharField(required=False, allow_blank=True)
    return_signature = serializers.CharField(required=False, allow_blank=True)
