from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import Account
import uuid


class Category(models.Model):
    """Categorías de materiales"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_consumable = models.BooleanField(
        default=False, 
        help_text="Los materiales de esta categoría son consumibles (se manejan por stock y no se devuelven)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
        unique_together = ['account', 'name']
        indexes = [
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['account', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.account.company_name})"


class Location(models.Model):
    """Almacenes o ubicaciones físicas de la empresa"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Dirección completa
    street = models.CharField(max_length=255)
    exterior_number = models.CharField(max_length=50)
    interior_number = models.CharField(max_length=50, blank=True, null=True)
    neighborhood = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='México')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['name']
        indexes = [
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['account', 'name']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"

    @property
    def full_address(self):
        """Retorna la dirección completa formateada"""
        parts = [self.street, self.exterior_number]
        if self.interior_number:
            parts.append(f"Int. {self.interior_number}")
        parts.extend([self.neighborhood, f"C.P. {self.postal_code}", self.city, self.state, self.country])
        return ', '.join(parts)


class Material(models.Model):
    """Materiales/Equipos disponibles para préstamo"""
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('on_loan', 'En préstamo'),
        ('maintenance', 'En mantenimiento'),
        ('damaged', 'Dañado'),
        ('retired', 'Retirado'),
    ]
    
    UNIT_CHOICES = [
        ('unit', 'Unidad'),
        ('set', 'Conjunto'),
        ('box', 'Caja'),
        ('package', 'Paquete'),
        ('meter', 'Metro'),
        ('kg', 'Kilogramo'),
        ('liter', 'Litro'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='materials')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='materials')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    
    # Información básica
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    
    # Código QR único generado automáticamente
    # Para consumibles: QR por lote
    # Para materiales regulares: QR individual
    qr_code = models.CharField(max_length=100, unique=True, editable=False)
    
    # Inventario
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    available_quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    unit_of_measure = models.CharField(max_length=50, choices=UNIT_CHOICES, default='unit')
    min_stock_level = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text="Nivel mínimo de stock. Alerta cuando available_quantity <= min_stock_level"
    )
    reorder_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad sugerida para reordenar cuando stock esté bajo"
    )
    
    # Imagen (S3)
    image_url = models.URLField(blank=True, null=True)
    
    # Estado y configuración
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    is_available_for_loan = models.BooleanField(default=True)
    requires_facial_auth = models.BooleanField(default=False, help_text="Requiere autenticación facial para préstamos")
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['name']
        indexes = [
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['account', 'category']),
            models.Index(fields=['account', 'location']),
            models.Index(fields=['qr_code']),
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['is_available_for_loan']),
        ]

    def __str__(self):
        return f"{self.name} - SKU: {self.sku}"
    
    @property
    def is_consumable(self):
        """Determina si el material es consumible basado en su categoría"""
        return self.category.is_consumable if self.category else False

    def save(self, *args, **kwargs):
        # Generar QR code único si no existe
        if not self.qr_code:
            self.qr_code = f"MAT-{uuid.uuid4().hex[:12].upper()}"
        
        # Actualizar available_quantity basado en el status
        if self.status in ['damaged', 'retired', 'maintenance']:
            self.available_quantity = 0
            self.is_available_for_loan = False
        
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return self.available_quantity <= self.min_stock_level

    @property
    def can_be_loaned(self):
        """Verifica si el material puede ser prestado"""
        return (
            self.is_active and 
            self.is_available_for_loan and 
            self.status == 'available' and 
            self.available_quantity > 0
        )
    
    @property
    def needs_reorder(self):
        """Verifica si se necesita reordenar (para consumibles)"""
        return self.is_consumable and self.is_low_stock
    
    def consume(self, quantity):
        """Reduce el stock de un consumible (no se devuelve)"""
        if not self.is_consumable:
            raise ValueError("Este material no es consumible")
        
        if quantity > self.available_quantity:
            raise ValueError(
                f"Stock insuficiente para {self.name}. "
                f"Disponible: {self.available_quantity}, Solicitado: {quantity}"
            )
        
        self.available_quantity -= quantity
        self.quantity -= quantity
        
        if self.available_quantity == 0:
            self.status = 'retired'
            self.is_available_for_loan = False
        
        self.save()
    
    def return_material(self, quantity=1):
        """Devolver material no-consumible (incrementa available_quantity)"""
        if self.is_consumable:
            raise ValueError("Los consumibles no se devuelven")
        
        self.available_quantity += quantity
        if self.available_quantity > self.quantity:
            self.available_quantity = self.quantity
        
        if self.status == 'on_loan' and self.available_quantity == self.quantity:
            self.status = 'available'
        
        self.save()
