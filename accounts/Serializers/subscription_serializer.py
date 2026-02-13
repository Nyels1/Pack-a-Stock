from rest_framework import serializers
from accounts.models import SubscriptionPlan, Payment, Account
from datetime import timedelta
from django.utils import timezone


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'display_name', 'price', 'duration_days',
            'max_users', 'max_locations', 'is_active'
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.display_name', read_only=True)
    account_name = serializers.CharField(source='account.company_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'account', 'plan', 'plan_name', 'account_name',
            'amount', 'card_last_four', 'card_holder_name',
            'status', 'paid_at', 'created_at'
        ]
        read_only_fields = fields


class SubscribeSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    card_number = serializers.CharField(max_length=19)
    card_holder = serializers.CharField(max_length=255)
    expiry = serializers.CharField(max_length=5)
    cvv = serializers.CharField(max_length=4)

    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError('Plan no encontrado o no disponible')
        return value

    def validate_card_number(self, value):
        cleaned = value.replace(' ', '').replace('-', '')
        if len(cleaned) < 13 or len(cleaned) > 19:
            raise serializers.ValidationError('Numero de tarjeta invalido')
        return cleaned

    def create(self, validated_data):
        account = self.context['account']
        plan = SubscriptionPlan.objects.get(id=validated_data['plan_id'])

        # Simulated payment - always succeeds
        card_number = validated_data['card_number']
        payment = Payment.objects.create(
            account=account,
            plan=plan,
            amount=plan.price,
            card_last_four=card_number[-4:],
            card_holder_name=validated_data['card_holder'],
            status='completed',
        )

        # Update account subscription
        today = timezone.now().date()
        account.subscription_plan = plan.name
        account.max_users = plan.max_users
        account.max_locations = plan.max_locations
        account.subscription_start_date = today
        account.subscription_end_date = today + timedelta(days=plan.duration_days)
        account.save()

        return payment
