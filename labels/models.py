from django.db import models
from accounts.models import Account


class LabelTemplate(models.Model):
    """Plantillas personalizadas para etiquetas QR"""
    
    LAYOUT_CHOICES = [
        ('standard', 'Estándar'),
        ('compact', 'Compacto'),
        ('detailed', 'Detallado'),
        ('custom', 'Personalizado'),
    ]
    
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='label_templates'
    )
    
    name = models.CharField(max_length=255)
    
    # Logo para la etiqueta (URL de S3)
    logo_url = models.URLField(blank=True, null=True)
    
    # Configuración del layout en JSON
    layout = models.JSONField(
        default=dict,
        help_text="""
        Estructura JSON del layout:
        {
            "type": "standard",
            "show_logo": true,
            "show_company_name": true,
            "show_material_name": true,
            "show_sku": true,
            "show_category": true,
            "show_location": true,
            "qr_size": "medium",
            "text_size": "small",
            "custom_fields": ["field1", "field2"]
        }
        """
    )
    
    # Template por defecto para la cuenta
    is_default = models.BooleanField(default=False)
    
    # Dimensiones de la etiqueta (en mm)
    width_mm = models.IntegerField(default=50, help_text="Ancho en milímetros")
    height_mm = models.IntegerField(default=30, help_text="Alto en milímetros")
    
    # Configuración de impresión
    print_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="""
        Configuración de impresión:
        {
            "dpi": 300,
            "paper_size": "A4",
            "labels_per_sheet": 21,
            "margin_top": 10,
            "margin_left": 10,
            "margin_right": 10,
            "margin_bottom": 10
        }
        """
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Etiqueta'
        verbose_name_plural = 'Plantillas de Etiquetas'
        ordering = ['-is_default', 'name']
        indexes = [
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['account', 'is_default']),
        ]
    
    def __str__(self):
        default_indicator = " (Por defecto)" if self.is_default else ""
        return f"{self.name}{default_indicator} - {self.account.company_name}"
    
    def save(self, *args, **kwargs):
        # Si se marca como default, quitar el default de las demás
        if self.is_default:
            LabelTemplate.objects.filter(
                account=self.account,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def get_default_layout(self):
        """Retorna un layout por defecto si no existe"""
        if not self.layout:
            return {
                "type": "standard",
                "show_logo": True,
                "show_company_name": True,
                "show_material_name": True,
                "show_sku": True,
                "show_category": False,
                "show_location": False,
                "qr_size": "medium",
                "text_size": "small",
                "custom_fields": []
            }
        return self.layout
    
    def get_default_print_settings(self):
        """Retorna configuración de impresión por defecto"""
        if not self.print_settings:
            return {
                "dpi": 300,
                "paper_size": "A4",
                "labels_per_sheet": 21,
                "margin_top": 10,
                "margin_left": 10,
                "margin_right": 10,
                "margin_bottom": 10
            }
        return self.print_settings
