from rest_framework import serializers
from materials.models import Material
from materials.Serializers.category_serializer import CategorySerializer
from materials.Serializers.location_serializer import LocationSerializer


class MaterialSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    location_detail = LocationSerializer(source='location', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    is_consumable = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    can_be_loaned = serializers.ReadOnlyField()
    needs_reorder = serializers.ReadOnlyField()
    next_available_date = serializers.SerializerMethodField()

    def get_next_available_date(self, obj):
        if obj.available_quantity > 0:
            return None
        from loans.models import Loan
        loan = Loan.objects.filter(
            material=obj,
            status__in=['active', 'overdue'],
            is_consumable_loan=False,
            expected_return_date__isnull=False
        ).order_by('expected_return_date').values_list('expected_return_date', flat=True).first()
        return loan

    class Meta:
        model = Material
        fields = [
            'id', 'account', 'category', 'category_detail', 'location', 'location_detail',
            'name', 'description', 'sku', 'barcode', 'serial_number', 'qr_code', 'qr_image',
            'quantity', 'available_quantity', 'unit_of_measure', 'min_stock_level',
            'reorder_quantity', 'image', 'image_url', 'status', 'is_available_for_loan',
            'requires_facial_auth', 'is_active', 'is_consumable', 'is_low_stock',
            'can_be_loaned', 'needs_reorder', 'next_available_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'account', 'qr_code', 'qr_image', 'available_quantity', 'is_consumable',
            'is_low_stock', 'can_be_loaned', 'needs_reorder', 'next_available_date',
            'created_at', 'updated_at'
        ]


class MaterialCreateSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Material
        fields = [
            'category', 'location', 'name', 'description', 'sku',
            'barcode', 'serial_number', 'quantity', 'unit_of_measure', 'min_stock_level',
            'reorder_quantity', 'image', 'image_url', 'status', 'is_available_for_loan',
            'requires_facial_auth'
        ]
        read_only_fields = []

    def create(self, validated_data):
        # available_quantity debe coincidir con quantity al crear
        validated_data['available_quantity'] = validated_data.get('quantity', 1)
        return super().create(validated_data)


class MaterialMinimalSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    category = CategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    next_available_date = serializers.SerializerMethodField()

    def get_next_available_date(self, obj):
        if obj.available_quantity > 0:
            return None
        from loans.models import Loan
        loan = Loan.objects.filter(
            material=obj,
            status__in=['active', 'overdue'],
            is_consumable_loan=False,
            expected_return_date__isnull=False
        ).order_by('expected_return_date').values_list('expected_return_date', flat=True).first()
        return loan

    class Meta:
        model = Material
        fields = [
            'id', 'name', 'sku', 'serial_number', 'qr_code', 'qr_image', 'image',
            'category', 'category_name', 'location', 'location_name',
            'quantity', 'available_quantity', 'status', 'is_available_for_loan', 'is_low_stock',
            'unit_of_measure', 'min_stock_level', 'description', 'is_consumable',
            'next_available_date'
        ]
