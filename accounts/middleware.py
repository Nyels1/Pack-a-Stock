from django.utils import timezone


class SubscriptionExpiryMiddleware:
    """
    Verifica en cada request si la suscripción del usuario ha vencido.
    Si venció, hace downgrade automático a freemium (max_locations=1, max_users=5).
    Los datos existentes NO se borran — solo se bloquea el exceso.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            account = request.user.account
            if (
                account.subscription_plan != 'freemium'
                and account.subscription_end_date is not None
                and account.subscription_end_date < timezone.now().date()
            ):
                account.subscription_plan = 'freemium'
                account.max_locations = 1
                account.max_users = 5
                account.subscription_start_date = None
                account.subscription_end_date = None
                account.save(update_fields=[
                    'subscription_plan', 'max_locations', 'max_users',
                    'subscription_start_date', 'subscription_end_date',
                ])

        return self.get_response(request)
