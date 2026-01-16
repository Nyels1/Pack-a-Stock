from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import Account, User
from materials.models import Material


class LoanRequest(models.Model):
    """Solicitudes de préstamo de materiales"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loan_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_requests')
    
    # Fechas y motivo
    requested_date = models.DateTimeField(auto_now_add=True)
    desired_pickup_date = models.DateField()
    desired_return_date = models.DateField()
    purpose = models.TextField(blank=True, null=True, help_text="Propósito del préstamo")
    
    # Estado y revisión
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_loan_requests',
        limit_choices_to={'user_type': 'inventarista'}
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de Préstamo'
        verbose_name_plural = 'Solicitudes de Préstamo'
        ordering = ['-requested_date']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['desired_pickup_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Solicitud #{self.id} - {self.requester.full_name} ({self.get_status_display()})"

    def approve(self, inventarista, notes=''):
        """Aprobar la solicitud"""
        self.status = 'approved'
        self.reviewed_by = inventarista
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()

    def reject(self, inventarista, notes=''):
        """Rechazar la solicitud"""
        self.status = 'rejected'
        self.reviewed_by = inventarista
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()


class LoanRequestItem(models.Model):
    """Items/Materiales solicitados en una solicitud de préstamo"""
    
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='loan_request_items')
    quantity_requested = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item de Solicitud'
        verbose_name_plural = 'Items de Solicitud'
        unique_together = ['loan_request', 'material']
        indexes = [
            models.Index(fields=['loan_request']),
            models.Index(fields=['material']),
        ]

    def __str__(self):
        return f"{self.material.name} x{self.quantity_requested} - Solicitud #{self.loan_request.id}"
    
    def clean(self):
        """Validar que hay suficiente stock para consumibles"""
        super().clean()
        if self.material.is_consumable:
            if self.quantity_requested > self.material.available_quantity:
                raise ValidationError(
                    f"Stock insuficiente para {self.material.name}. "
                    f"Disponible: {self.material.available_quantity}, Solicitado: {self.quantity_requested}"
                )
    
    def save(self, *args, **kwargs):
        """Validar antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)


class Loan(models.Model):
    """Préstamos activos de materiales"""
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('returned', 'Devuelto'),
        ('overdue', 'Vencido'),
        ('lost', 'Extraviado'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Malo'),
        ('damaged', 'Dañado'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    loan_request = models.ForeignKey(
        LoanRequest, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='loans'
    )
    
    # Usuarios involucrados
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_loans')
    issued_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='issued_loans',
        limit_choices_to={'user_type': 'inventarista'}
    )
    returned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='received_returns',
        limit_choices_to={'user_type': 'inventarista'}
    )
    
    # Material prestado
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='loans')
    quantity_loaned = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    quantity_returned = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Consumibles (no se devuelven)
    is_consumable_loan = models.BooleanField(
        default=False,
        help_text="Si es consumible, se reduce el stock permanentemente y no requiere devolución"
    )
    
    # Fechas
    issued_at = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)  # Null para consumibles
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    # Autenticación facial
    facial_auth_verified = models.BooleanField(default=False)
    facial_auth_at = models.DateTimeField(null=True, blank=True)
    
    # Firmas digitales
    pickup_signature = models.TextField(blank=True, null=True, help_text="Firma digital en base64")
    return_signature = models.TextField(blank=True, null=True, help_text="Firma digital en base64")
    
    # Condiciones del material
    condition_on_pickup = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='good')
    condition_on_return = models.CharField(max_length=50, choices=CONDITION_CHOICES, null=True, blank=True)
    damage_notes = models.TextField(blank=True, null=True)
    
    # Estado
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['borrower', 'status']),
            models.Index(fields=['material', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_return_date']),
            models.Index(fields=['loan_request']),
        ]

    def __str__(self):
        return f"Préstamo #{self.id} - {self.material.name} a {self.borrower.full_name}"

    def save(self, *args, **kwargs):
        # Establecer is_consumable_loan basado en el material
        if self.material:
            self.is_consumable_loan = self.material.is_consumable
            
            # Si es consumible, no tiene fecha de retorno y marca como devuelto automáticamente
            if self.is_consumable_loan:
                self.expected_return_date = None
                self.status = 'returned'  # Los consumibles se marcan como "entregados" inmediatamente
                self.quantity_returned = self.quantity_loaned
                
                # Reducir stock del material permanentemente
                self.material.consume(self.quantity_loaned)
        
        # Actualizar estado a vencido si pasó la fecha de retorno (solo no-consumibles)
        if not self.is_consumable_loan and self.status == 'active' and self.expected_return_date:
            if self.expected_return_date < timezone.now().date():
                self.status = 'overdue'
        
        super().save(*args, **kwargs)
        
        # Actualizar cantidad disponible del material (solo no-consumibles)
        if not self.is_consumable_loan:
            self.update_material_availability()

    def update_material_availability(self):
        """Actualizar la cantidad disponible del material"""
        material = self.material
        
        # Calcular cantidad total prestada activa
        active_loans = Loan.objects.filter(
            material=material,
            status__in=['active', 'overdue']
        ).aggregate(
            total=models.Sum('quantity_loaned')
        )['total'] or 0
        
        # Actualizar cantidad disponible
        material.available_quantity = material.quantity - active_loans
        
        # Actualizar estado del material
        if material.available_quantity <= 0:
            material.status = 'on_loan'
        elif material.status == 'on_loan' and material.available_quantity > 0:
            material.status = 'available'
        
        material.save()

    def return_loan(self, inventarista, condition, damage_notes='', signature=''):
        """Registrar la devolución del préstamo (solo no-consumibles)"""
        if self.is_consumable_loan:
            raise ValueError("Los consumibles no se devuelven, se consumen al entregarlos")
        
        self.status = 'returned'
        self.actual_return_date = timezone.now()
        self.returned_to = inventarista
        self.condition_on_return = condition
        self.damage_notes = damage_notes
        self.return_signature = signature
        self.quantity_returned = self.quantity_loaned
        self.save()
        
        # Devolver al inventario
        self.material.return_material(self.quantity_loaned)
        
        # Si está dañado, actualizar material
        if condition == 'damaged':
            self.material.status = 'damaged'
            self.material.save()

    @property
    def is_overdue(self):
        """Verifica si el préstamo está vencido (solo no-consumibles)"""
        if self.is_consumable_loan:
            return False
        return self.status == 'active' and self.expected_return_date < timezone.now().date()

    @property
    def days_until_return(self):
        """Días hasta la fecha de retorno (negativo si está vencido)"""
        if self.is_consumable_loan or not self.expected_return_date:
            return 0
        delta = self.expected_return_date - timezone.now().date()
        return delta.days

    @property
    def is_fully_returned(self):
        """Verifica si se devolvió toda la cantidad prestada"""
        return self.quantity_returned >= self.quantity_loaned


class LoanExtension(models.Model):
    """Extensiones/Prórrogas de préstamos"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='extensions')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extension_requests')
    
    # Solicitud
    requested_at = models.DateTimeField(auto_now_add=True)
    new_return_date = models.DateField()
    reason = models.TextField()
    
    # Revisión
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_extensions',
        limit_choices_to={'user_type': 'inventarista'}
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Extensión de Préstamo'
        verbose_name_plural = 'Extensiones de Préstamo'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['loan', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Extensión #{self.id} - Préstamo #{self.loan.id} ({self.get_status_display()})"

    def approve(self, inventarista, notes=''):
        """Aprobar la extensión"""
        self.status = 'approved'
        self.reviewed_by = inventarista
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
        
        # Actualizar fecha de retorno del préstamo
        self.loan.expected_return_date = self.new_return_date
        if self.loan.status == 'overdue':
            self.loan.status = 'active'
        self.loan.save()

    def reject(self, inventarista, notes=''):
        """Rechazar la extensión"""
        self.status = 'rejected'
        self.reviewed_by = inventarista
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()

