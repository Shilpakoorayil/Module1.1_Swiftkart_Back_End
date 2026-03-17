from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserLoginView, AdminLoginView, GuestLoginView, 
                    ClosestStoreView, ProductViewSet, AddressViewSet, CheckoutView)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('auth/login/user/', UserLoginView.as_view(), name='user-login'),
    path('auth/login/admin/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/login/guest/', GuestLoginView.as_view(), name='guest-login'),
    path('location/closest-store/', ClosestStoreView.as_view(), name='closest-store'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', include(router.urls)),
]
