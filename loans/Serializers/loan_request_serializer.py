from rest_framework import serializers
from loans.models import LoanRequest, LoanRequestItem
from accounts.Serializers.user_serializer import UserSerializer
from materials.Serializers.material_serializer import MaterialMinimalSerializer


class LoanRequestItemSerializer(serializers.ModelSerializer):
    material_detail = MaterialMinimalSerializer(source='material', read_only=True)
    
    class Meta:
        model = LoanRequestItem
        fields = ['id', 'material', 'material_detail', 'quantity_requested', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoanRequestSerializer(serializers.ModelSerializer):
    requester_detail = UserSerializer(source='requester', read_only=True)
    reviewed_by_detail = UserSerializer(source='reviewed_by', read_only=True)
    items = LoanRequestItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = LoanRequest
        fields = [
            'id', 'account', 'requester', 'requester_detail', 'requested_date',
            'desired_pickup_date', 'desired_return_date', 'purpose', 'status',
            'reviewed_by', 'reviewed_by_detail', 'reviewed_at', 'review_notes',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requested_date', 'reviewed_by', 'reviewed_at', 
            'created_at', 'updated_at'
        ]


class LoanRequestCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = LoanRequest
        fields = [
            'desired_pickup_date', 'desired_return_date', 'purpose', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        loan_request = LoanRequest.objects.create(**validated_data)
        
        # Crear items
        for item_data in items_data:
            LoanRequestItem.objects.create(
                loan_request=loan_request,
                material_id=item_data['material_id'],
                quantity_requested=item_data.get('quantity_requested', 1)
            )
        
        return loan_request
