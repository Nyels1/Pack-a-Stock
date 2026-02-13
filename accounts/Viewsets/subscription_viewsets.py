from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import SubscriptionPlan, Payment
from accounts.Serializers.subscription_serializer import (
    SubscriptionPlanSerializer,
    PaymentSerializer,
    SubscribeSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_plans(request):
    """List all active subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request):
    """Subscribe to a plan (simulated payment)"""
    if request.user.user_type != 'inventarista':
        return Response({
            'success': False,
            'message': 'Solo los inventaristas pueden gestionar suscripciones'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = SubscribeSerializer(
        data=request.data,
        context={'account': request.user.account}
    )
    if serializer.is_valid():
        payment = serializer.save()
        return Response({
            'success': True,
            'message': 'Suscripcion activada exitosamente',
            'data': PaymentSerializer(payment).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Get payment history for the account"""
    payments = Payment.objects.filter(account=request.user.account)
    serializer = PaymentSerializer(payments, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Get current subscription status"""
    account = request.user.account
    return Response({
        'success': True,
        'data': {
            'subscription_plan': account.subscription_plan,
            'max_users': account.max_users,
            'max_locations': account.max_locations,
            'subscription_start_date': account.subscription_start_date,
            'subscription_end_date': account.subscription_end_date,
            'is_active': account.is_active,
        }
    })
