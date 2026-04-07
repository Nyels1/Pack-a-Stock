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
from loans.models import Loan
from accounts.Serializers.user_serializer import UserSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ['category', 'location', 'status', 'is_available_for_loan', 'is_active']
    search_fields = ['name', 'description', 'sku', 'barcode', 'qr_code']
    ordering_fields = ['name', 'sku', 'quantity', 'available_quantity', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Material.objects.filter(account=user.account).select_related('category', 'location', 'account')

    def _get_locked_location_ids(self, account):
        from materials.models import Location
        if account.max_locations == -1:
            return set()
        ids = list(
            Location.objects.filter(account=account)
            .order_by('created_at')
            .values_list('id', flat=True)
        )
        if len(ids) <= account.max_locations:
            return set()
        return set(ids[account.max_locations:])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['locked_location_ids'] = self._get_locked_location_ids(self.request.user.account)
        return context

    def get_serializer_class(self):
        if self.action == 'create':
            return MaterialCreateSerializer
        elif self.action == 'list':
            return MaterialMinimalSerializer
        return MaterialSerializer
    
    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account)

    def perform_update(self, serializer):
        instance = self.get_object()
        new_quantity = serializer.validated_data.get('quantity', instance.quantity)
        diff = new_quantity - instance.quantity
        new_available = max(0, instance.available_quantity + diff)
        serializer.save(available_quantity=new_available)

    def perform_destroy(self, instance):
        from audit.models import AuditLog
        from loans.models import Loan
        # Snapshot loan history before CASCADE deletes them
        loans_qs = Loan.objects.filter(material=instance).select_related('borrower').order_by('-issued_at')
        loan_history = [
            {
                'id': loan.id,
                'borrower': loan.borrower.full_name if loan.borrower else 'N/A',
                'quantity': loan.quantity_loaned,
                'issued_at': str(loan.issued_at)[:10] if loan.issued_at else None,
                'returned_at': str(loan.actual_return_date) if loan.actual_return_date else None,
                'status': loan.status,
            }
            for loan in loans_qs[:50]
        ]
        AuditLog.log_action(
            action='delete',
            user=self.request.user,
            account=instance.account,
            table_name='material',
            record_id=instance.id,
            changes={
                'snapshot': {
                    'name': instance.name,
                    'sku': instance.sku,
                    'category': instance.category.name if instance.category else None,
                    'quantity': instance.quantity,
                    'available_quantity': instance.available_quantity,
                    'status': instance.status,
                    'location': instance.location.name if instance.location else None,
                    'total_loans': loans_qs.count(),
                    'loan_history': loan_history,
                }
            },
            ip_address=self.request.META.get('REMOTE_ADDR'),
            description=f'Material "{instance.name}" (SKU: {instance.sku}) eliminado',
        )
        instance.delete()
    
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
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Agregar stock a un material consumible"""
        material = self.get_object()
        quantity = request.data.get('quantity', 0)

        if not material.is_consumable:
            return Response(
                {'error': 'Solo se puede agregar stock a materiales consumibles'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(quantity, int) or quantity <= 0:
            return Response(
                {'error': 'La cantidad debe ser un número entero mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        material.quantity += quantity
        material.available_quantity += quantity

        if material.status in ('retired',) and material.available_quantity > 0:
            material.status = 'available'
            material.is_available_for_loan = True

        material.save()

        return Response({
            'status': 'success',
            'message': f'{quantity} unidades agregadas al stock',
            'quantity': material.quantity,
            'available_quantity': material.available_quantity
        })

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

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get loan history for a specific material"""
        material = self.get_object()
        loans = Loan.objects.filter(
            material=material
        ).select_related('borrower', 'issued_by').order_by('-issued_at')

        history_data = []
        for loan in loans:
            duration_days = None
            if loan.actual_return_date and loan.issued_at:
                duration_days = (loan.actual_return_date.date() - loan.issued_at.date()).days
            elif loan.status == 'active' and loan.issued_at:
                from django.utils import timezone
                duration_days = (timezone.now().date() - loan.issued_at.date()).days

            history_data.append({
                'id': loan.id,
                'borrower': {
                    'id': loan.borrower.id,
                    'full_name': loan.borrower.full_name,
                    'email': loan.borrower.email,
                },
                'quantity_loaned': loan.quantity_loaned,
                'issued_at': loan.issued_at,
                'expected_return_date': loan.expected_return_date,
                'actual_return_date': loan.actual_return_date,
                'status': loan.status,
                'condition_on_pickup': loan.condition_on_pickup,
                'condition_on_return': loan.condition_on_return,
                'duration_days': duration_days,
            })

        # Stats
        total_loans = loans.count()
        active_loans = loans.filter(status='active').count()
        from django.db.models import Count
        top_borrower = loans.values('borrower__full_name').annotate(
            count=Count('id')
        ).order_by('-count').first()

        return Response({
            'success': True,
            'data': {
                'material_name': material.name,
                'material_sku': material.sku,
                'total_loans': total_loans,
                'active_loans': active_loans,
                'top_borrower': top_borrower['borrower__full_name'] if top_borrower else None,
                'history': history_data,
            }
        })


from django.db import models
