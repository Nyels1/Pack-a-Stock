from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from materials.models import Material
from materials.Serializers.material_serializer import (
    MaterialSerializer,
    MaterialCreateSerializer,
    MaterialMinimalSerializer
)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'location', 'status', 'is_available_for_loan', 'is_active']
    search_fields = ['name', 'description', 'sku', 'barcode', 'qr_code']
    ordering_fields = ['name', 'sku', 'quantity', 'available_quantity', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Material.objects.filter(account=user.account)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MaterialCreateSerializer
        elif self.action == 'list':
            return MaterialMinimalSerializer
        return MaterialSerializer
    
    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Obtener materiales con stock bajo"""
        materials = self.get_queryset().filter(
            available_quantity__lte=models.F('min_stock_level')
        )
        serializer = self.get_serializer(materials, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def consumables(self, request):
        """Obtener solo materiales consumibles"""
        materials = self.get_queryset().filter(category__is_consumable=True)
        serializer = self.get_serializer(materials, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """Consumir unidades de un material consumible"""
        material = self.get_object()
        quantity = request.data.get('quantity', 1)
        
        try:
            material.consume(quantity)
            return Response({
                'status': 'success',
                'message': f'{quantity} unidades consumidas',
                'available_quantity': material.available_quantity
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Obtener información del código QR del material"""
        material = self.get_object()
        return Response({
            'qr_code': material.qr_code,
            'qr_image': material.qr_image.url if material.qr_image else None,
            'material': MaterialMinimalSerializer(material).data
        })
    
    @action(detail=False, methods=['get'])
    def search_by_qr(self, request):
        """Buscar material por código QR"""
        qr_code = request.query_params.get('qr_code')
        if not qr_code:
            return Response({'error': 'qr_code parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            material = self.get_queryset().get(qr_code=qr_code)
            serializer = self.get_serializer(material)
            return Response(serializer.data)
        except Material.DoesNotExist:
            return Response({'error': 'Material no encontrado'}, status=status.HTTP_404_NOT_FOUND)


from django.db import models
