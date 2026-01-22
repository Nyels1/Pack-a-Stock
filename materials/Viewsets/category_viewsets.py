from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from materials.models import Category
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
