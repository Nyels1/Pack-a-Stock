from django.db import models
from accounts.models import Account, User


class AuditLog(models.Model):
    """Registro de auditoría de todas las acciones del sistema"""
    
    ACTION_CHOICES = [
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('approve', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('loan_issue', 'Préstamo emitido'),
        ('loan_return', 'Préstamo devuelto'),
        ('extension_request', 'Solicitud de extensión'),
        ('extension_approved', 'Extensión aprobada'),
        ('extension_rejected', 'Extensión rechazada'),
        ('material_consume', 'Material consumido'),
        ('stock_update', 'Actualización de stock'),
    ]
    
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Acción realizada
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    
    # Información del registro afectado
    table_name = models.CharField(max_length=100, blank=True, null=True)
    record_id = models.IntegerField(blank=True, null=True)
    
    # Cambios realizados (JSON)
    changes = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON con los cambios: {campo: {old: valor_anterior, new: valor_nuevo}}"
    )
    
    # Metadatos de la acción
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Descripción adicional
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['table_name', 'record_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_info = f"{self.user.full_name}" if self.user else "Sistema"
        return f"{self.action} - {user_info} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_action(cls, action, user=None, account=None, table_name=None, 
                   record_id=None, changes=None, ip_address=None, 
                   user_agent=None, description=None):
        """
        Método helper para crear logs de auditoría
        
        Ejemplo:
        AuditLog.log_action(
            action='loan_issue',
            user=request.user,
            account=loan.account,
            table_name='loans',
            record_id=loan.id,
            changes={'status': {'old': 'pending', 'new': 'active'}},
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'Préstamo #{loan.id} emitido'
        )
        """
        return cls.objects.create(
            action=action,
            user=user,
            account=account or (user.account if user else None),
            table_name=table_name,
            record_id=record_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description
        )
