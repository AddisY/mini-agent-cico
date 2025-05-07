from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommissionRateViewSet, CommissionTransactionViewSet

router = DefaultRouter()
router.register(r'commission-rates', CommissionRateViewSet)
router.register(r'commission-records', CommissionTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 