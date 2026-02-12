"""
URL configuration for pack_a_stock_api project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Importar routers de cada app
from accounts.routers import router as accounts_router
from materials.routers import router as materials_router
from loans.routers import router as loans_router

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API principal con routers modularizados
    path('api/accounts/', include(accounts_router.urls)),
    path('api/materials/', include(materials_router.urls)),
    path('api/loans/', include(loans_router.urls)),
    
    # Autenticación REST Framework
    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos media en desarrollo (si no se usa S3)
if settings.DEBUG and not settings.AWS_ACCESS_KEY_ID:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

