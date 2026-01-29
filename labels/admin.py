from django.contrib import admin
from .models import LabelTemplate


@admin.register(LabelTemplate)
class LabelTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'account', 'is_default', 'width_mm', 'height_mm', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'account', 'created_at']
    search_fields = ['name', 'account__company_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'name', 'logo_url', 'is_default', 'is_active')
        }),
        ('Dimensiones', {
            'fields': ('width_mm', 'height_mm')
        }),
        ('Configuración de Layout', {
            'fields': ('layout',),
            'classes': ('collapse',)
        }),
        ('Configuración de Impresión', {
            'fields': ('print_settings',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
