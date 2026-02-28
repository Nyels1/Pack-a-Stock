from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from audit.models import AuditLog
from audit.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'table_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = AuditLog.objects.filter(account=self.request.user.account)
        # Optional ?since= filter (ISO date string)
        since = self.request.query_params.get('since')
        if since:
            qs = qs.filter(created_at__gte=since)
        return qs
