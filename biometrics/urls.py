from django.urls import path
from .views import EnrollView, StatusView, VerifyView

urlpatterns = [
    path('enroll/', EnrollView.as_view(), name='biometric-enroll'),
    path('verify/', VerifyView.as_view(), name='biometric-verify'),
    path('status/', StatusView.as_view(), name='biometric-status'),
]
