from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
        serializer.save(account=account)
