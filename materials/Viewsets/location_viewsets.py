from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from materials.models import Location
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
        return Location.objects.filter(account=user.account)

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
