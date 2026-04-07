from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from materials.models import Location, Material
from materials.Serializers.location_serializer import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'city', 'state']
    search_fields = ['name', 'description', 'city', 'state']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        user = self.request.user
        return Location.objects.filter(account=user.account).order_by('created_at')

    def _get_locked_ids(self, account):
        """Retorna el set de IDs de ubicaciones bloqueadas por exceder el límite del plan.
        Las más recientes (por created_at) son las que se bloquean primero."""
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
            context['locked_ids'] = self._get_locked_ids(self.request.user.account)
        return context

    def perform_create(self, serializer):
        account = self.request.user.account
        current_locations = Location.objects.filter(account=account).count()

        if account.max_locations != -1 and current_locations >= account.max_locations:
            raise ValidationError({
                'error': 'LOCATIONS_LIMIT_REACHED',
                'message': f'Has alcanzado el límite de ubicaciones para tu plan ({account.max_locations})',
                'details': {
                    'current_plan': account.subscription_plan,
                    'max_locations': account.max_locations,
                    'current_locations': current_locations
                }
            })

        serializer.save(account=account)

    def perform_destroy(self, instance):
        from audit.models import AuditLog
        from materials.models import Material
        materials_count = Material.objects.filter(location=instance).count()
        AuditLog.log_action(
            action='delete',
            user=self.request.user,
            account=instance.account,
            table_name='location',
            record_id=instance.id,
            changes={
                'snapshot': {
                    'name': instance.name,
                    'description': instance.description,
                    'full_address': instance.full_address,
                    'materials_count': materials_count,
                }
            },
            ip_address=self.request.META.get('REMOTE_ADDR'),
            description=f'Ubicación "{instance.name}" eliminada',
        )
        instance.delete()

    @action(detail=True, methods=['get'])
    def check_delete(self, request, pk=None):
        location = self.get_object()
        materials = Material.objects.filter(location=location)
        return Response({
            'can_delete': True,
            'materials_count': materials.count(),
            'material_names': list(materials.values_list('name', flat=True)[:10]),
        })
