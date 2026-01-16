from django.contrib import admin
from .models import LoanRequest, LoanRequestItem, Loan, LoanExtension


class LoanRequestItemInline(admin.TabularInline):
    model = LoanRequestItem
    extra = 0
    fields = ['material', 'quantity_requested']
    autocomplete_fields = ['material']


@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'requester', 'account', 'status',
        'desired_pickup_date', 'desired_return_date',
        'requested_date', 'reviewed_by'
    ]
    list_filter = ['status', 'account', 'desired_pickup_date', 'requested_date']
    search_fields = [
        'requester__full_name', 'requester__email',
        'purpose', 'review_notes', 'account__company_name'
    ]
    readonly_fields = ['requested_date', 'reviewed_at', 'created_at', 'updated_at']
    inlines = [LoanRequestItemInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'requester', 'purpose')
        }),
        ('Fechas Solicitadas', {
            'fields': ('desired_pickup_date', 'desired_return_date')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Revisión', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Fechas del Sistema', {
            'fields': ('requested_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        count = 0
        for loan_request in queryset.filter(status='pending'):
            loan_request.approve(request.user, 'Aprobado desde admin')
            count += 1
        self.message_user(request, f'{count} solicitudes aprobadas')
    approve_requests.short_description = 'Aprobar solicitudes seleccionadas'
    
    def reject_requests(self, request, queryset):
        count = 0
        for loan_request in queryset.filter(status='pending'):
            loan_request.reject(request.user, 'Rechazado desde admin')
            count += 1
        self.message_user(request, f'{count} solicitudes rechazadas')
    reject_requests.short_description = 'Rechazar solicitudes seleccionadas'


@admin.register(LoanRequestItem)
class LoanRequestItemAdmin(admin.ModelAdmin):
    list_display = ['loan_request', 'material', 'quantity_requested', 'created_at']
    list_filter = ['loan_request__status', 'material__category']
    search_fields = ['material__name', 'loan_request__requester__full_name']
    autocomplete_fields = ['material', 'loan_request']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'borrower', 'material', 'quantity_loaned',
        'is_consumable_loan', 'status', 'issued_at',
        'expected_return_date', 'actual_return_date'
    ]
    list_filter = [
        'status', 'is_consumable_loan', 'account',
        'issued_at', 'expected_return_date'
    ]
    search_fields = [
        'borrower__full_name', 'borrower__email',
        'material__name', 'material__sku',
        'account__company_name'
    ]
    readonly_fields = [
        'issued_at', 'actual_return_date', 'facial_auth_at',
        'created_at', 'updated_at', 'is_consumable_loan'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('account', 'loan_request', 'material', 'is_consumable_loan')
        }),
        ('Usuarios', {
            'fields': ('borrower', 'issued_by', 'returned_to')
        }),
        ('Cantidades', {
            'fields': ('quantity_loaned', 'quantity_returned')
        }),
        ('Fechas', {
            'fields': (
                'issued_at', 'expected_return_date', 'actual_return_date'
            )
        }),
        ('Autenticación Facial', {
            'fields': ('facial_auth_verified', 'facial_auth_at'),
            'classes': ('collapse',)
        }),
        ('Firmas', {
            'fields': ('pickup_signature', 'return_signature'),
            'classes': ('collapse',)
        }),
        ('Condiciones', {
            'fields': (
                'condition_on_pickup', 'condition_on_return', 'damage_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_consumable_loan(self, obj):
        return obj.is_consumable_loan
    is_consumable_loan.boolean = True
    is_consumable_loan.short_description = '¿Consumible?'


@admin.register(LoanExtension)
class LoanExtensionAdmin(admin.ModelAdmin):
    list_display = [
        'loan', 'requested_by', 'status',
        'new_return_date', 'requested_at', 'reviewed_by'
    ]
    list_filter = ['status', 'requested_at', 'reviewed_at']
    search_fields = [
        'loan__borrower__full_name', 'requested_by__full_name',
        'reason', 'review_notes'
    ]
    readonly_fields = ['requested_at', 'reviewed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('loan', 'requested_by', 'reason')
        }),
        ('Nueva Fecha de Retorno', {
            'fields': ('new_return_date',)
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Revisión', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Fechas del Sistema', {
            'fields': ('requested_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
