from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'documents', views.AgentDocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('validate-field/', views.validate_field, name='validate_field'),
] 