from rest_framework import routers
from loans.Viewsets.loan_request_viewsets import LoanRequestViewSet
from loans.Viewsets.loan_viewsets import LoanViewSet
from loans.Viewsets.loan_extension_viewsets import LoanExtensionViewSet


router = routers.DefaultRouter()
router.register(r'loan-requests', LoanRequestViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'loan-extensions', LoanExtensionViewSet)
