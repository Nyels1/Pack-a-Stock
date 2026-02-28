from rest_framework import serializers
from audit.models import AuditLog

TABLE_LABELS = {
    'material': 'Material',
    'category': 'Categoría',
    'location': 'Ubicación',
}

ACTION_LABELS = {
    'create': 'Crear',
    'update': 'Actualizar',
    'delete': 'Eliminar',
    'login': 'Inicio de sesión',
    'logout': 'Cierre de sesión',
    'approve': 'Aprobar',
    'reject': 'Rechazar',
    'loan_issue': 'Préstamo emitido',
    'loan_return': 'Préstamo devuelto',
    'extension_request': 'Solicitud de extensión',
    'extension_approved': 'Extensión aprobada',
    'extension_rejected': 'Extensión rechazada',
    'material_consume': 'Material consumido',
    'stock_update': 'Actualización de stock',
    'biometric_enroll': 'Registro biométrico',
    'biometric_verify_fail': 'Verificación biométrica fallida',
}


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    table_label = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_label',
            'table_name', 'table_label', 'record_id',
            'changes', 'description',
            'user_name', 'ip_address', 'created_at',
        ]

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else 'Sistema'

    def get_table_label(self, obj):
        return TABLE_LABELS.get(obj.table_name or '', obj.table_name or '')

    def get_action_label(self, obj):
        return ACTION_LABELS.get(obj.action, obj.action)
