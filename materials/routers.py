from rest_framework import routers
from materials.Viewsets.category_viewsets import CategoryViewSet
from materials.Viewsets.location_viewsets import LocationViewSet
from materials.Viewsets.material_viewsets import MaterialViewSet


router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'materials', MaterialViewSet)
