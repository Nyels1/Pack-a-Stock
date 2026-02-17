from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from materials.models import Category, Material
from materials.Serializers.category_serializer import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_consumable', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(account=user.account)

    def perform_create(self, serializer):
        account = self.request.user.account
        serializer.save(account=account)

    @action(detail=True, methods=['get'])
    def check_delete(self, request, pk=None):
        category = self.get_object()
        materials = Material.objects.filter(category=category)
        return Response({
            'can_delete': True,
            'materials_count': materials.count(),
            'material_names': list(materials.values_list('name', flat=True)[:10]),
        })
