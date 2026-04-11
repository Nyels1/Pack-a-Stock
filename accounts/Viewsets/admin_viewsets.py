from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import Account, User, Payment, SubscriptionPlan
from accounts.Serializers.account_serializer import AccountSerializer
from accounts.Serializers.user_serializer import UserSerializer
from accounts.Serializers.subscription_serializer import PaymentSerializer


class IsSuperUser(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


@api_view(['GET'])
@permission_classes([IsSuperUser])
def admin_stats(request):
    """Global statistics for admin dashboard"""
    total_accounts = Account.objects.count()
    active_accounts = Account.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    payments_this_month = Payment.objects.filter(
        status='completed',
        paid_at__month=timezone.now().month,
        paid_at__year=timezone.now().year,
    ).aggregate(total=Sum('amount'))['total'] or 0

    plan_distribution = {}
    for choice_value, choice_label in Account.PLAN_CHOICES:
        plan_distribution[choice_value] = Account.objects.filter(
            subscription_plan=choice_value
        ).count()

    recent_payments = Payment.objects.filter(
        status='completed'
    ).order_by('-paid_at')[:5]

    return Response({
        'success': True,
        'data': {
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'total_users': total_users,
            'active_users': active_users,
            'total_revenue': float(total_revenue),
            'payments_this_month': float(payments_this_month),
            'plan_distribution': plan_distribution,
            'recent_payments': PaymentSerializer(recent_payments, many=True).data,
        }
    })


@api_view(['GET'])
@permission_classes([IsSuperUser])
def admin_accounts(request):
    """List all accounts with stats"""
    accounts = Account.objects.annotate(
        user_count=Count('users'),
    ).order_by('-created_at')

    data = []
    for account in accounts:
        acc_data = AccountSerializer(account).data
        acc_data['user_count'] = account.user_count
        acc_data['payment_count'] = Payment.objects.filter(account=account).count()
        data.append(acc_data)

    return Response({
        'success': True,
        'data': data
    })


@api_view(['PATCH'])
@permission_classes([IsSuperUser])
def admin_update_account(request, pk):
    """Update an account (plan, limits, status)"""
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Cuenta no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

    allowed_fields = [
        'subscription_plan', 'max_users', 'max_locations',
        'is_active', 'subscription_start_date', 'subscription_end_date'
    ]
    for field in allowed_fields:
        if field in request.data:
            setattr(account, field, request.data[field])

    account.save()

    return Response({
        'success': True,
        'message': 'Cuenta actualizada exitosamente',
        'data': AccountSerializer(account).data
    })


@api_view(['GET'])
@permission_classes([IsSuperUser])
def admin_payments(request):
    """List all payments globally"""
    payments = Payment.objects.all().order_by('-paid_at')
    serializer = PaymentSerializer(payments, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsSuperUser])
def admin_users(request):
    """List all users globally"""
    users = User.objects.all().order_by('-created_at')
    serializer = UserSerializer(users, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsSuperUser])
def admin_toggle_user(request, pk):
    """Block or unblock a user"""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')  # 'block' or 'unblock'
    if action == 'block':
        user.is_active = False
        user.save()
        return Response({'success': True, 'message': 'Usuario bloqueado'})
    elif action == 'unblock':
        user.is_active = True
        user.save()
        return Response({'success': True, 'message': 'Usuario desbloqueado'})
    return Response({'success': False, 'message': 'Accion invalida'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsSuperUser])
def admin_delete_account(request, pk):
    """Delete an account and all its data"""
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({'success': False, 'message': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    company_name = account.company_name
    account.delete()
    return Response({'success': True, 'message': f'Cuenta {company_name} eliminada'})
