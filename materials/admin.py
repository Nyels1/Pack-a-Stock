from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Location, Material


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'is_consumable', 'is_active', 'created_at']
    list_filter = ['is_consumable', 'is_active', 'account']
    search_fields = ['name', 'description', 'account__company_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'name', 'description', 'is_consumable')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['is_active', 'account', 'state', 'city']
    search_fields = ['name', 'description', 'city', 'state', 'account__company_name']
    readonly_fields = ['created_at', 'updated_at', 'full_address']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'name', 'description')
        }),
        ('Dirección', {
            'fields': (
                'street', 'exterior_number', 'interior_number',
                'neighborhood', 'postal_code', 'city', 'state', 'country',
                'full_address'
            )
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'location', 'account',
        'is_consumable', 'quantity', 'available_quantity',
        'status', 'is_low_stock', 'created_at'
    ]
    list_filter = [
        'category__is_consumable', 'status', 'is_available_for_loan',
        'is_active', 'account', 'category', 'location'
    ]
    search_fields = ['name', 'description', 'sku', 'barcode', 'qr_code', 'account__company_name']
    readonly_fields = [
        'qr_code', 'qr_image', 'created_at', 'updated_at', 'is_consumable',
        'can_be_loaned', 'is_low_stock', 'needs_reorder'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'category', 'location', 'name', 'description')
        }),
        ('Códigos', {
            'fields': ('sku', 'barcode', 'qr_code', 'qr_image')
        }),
        ('Inventario', {
            'fields': (
                'quantity', 'available_quantity', 'unit_of_measure',
                'min_stock_level', 'reorder_quantity'
            )
        }),
        ('Estado y Disponibilidad', {
            'fields': (
                'status', 'is_available_for_loan', 'requires_facial_auth',
                'is_active', 'is_consumable', 'can_be_loaned',
                'is_low_stock', 'needs_reorder'
            )
        }),
        ('Multimedia', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_consumable(self, obj):
        return obj.is_consumable
    is_consumable.boolean = True
    is_consumable.short_description = '¿Es Consumible?'
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Stock Bajo'

    def qr_image(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="max-height:180px;"/>', obj.qr_image.url)
        return '-'
    qr_image.short_description = 'QR'
