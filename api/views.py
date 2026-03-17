from django.shortcuts import render
import math
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Store, Address, Product, Order, OrderItem
from .serializers import (UserSerializer, UserLoginSerializer, AdminLoginSerializer,
                          StoreSerializer, AddressSerializer, ProductSerializer, OrderSerializer)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = get_tokens_for_user(user)
            return Response({'tokens': tokens, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = get_tokens_for_user(user)
            return Response({'tokens': tokens, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Create a temporary guest user
        guest_mobile = f"guest_{User.objects.count() + 1}"
        guest_user = User.objects.create(username=guest_mobile, role='GUEST')
        tokens = get_tokens_for_user(guest_user)
        return Response({'tokens': tokens, 'user': UserSerializer(guest_user).data}, status=status.HTTP_200_OK)

def haversine(lat1, lon1, lat2, lon2):
    # Mock Haversine distance formula for store location matching
    R = 6371.0 # Radius of the Earth in km
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

class ClosestStoreView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if not lat or not lon:
            return Response({"error": "Latitude and Longitude are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        stores = Store.objects.all()
        if not stores.exists():
            return Response({"error": "No stores available"}, status=status.HTTP_404_NOT_FOUND)
        
        closest_store = min(stores, key=lambda s: haversine(float(lat), float(lon), s.latitude, s.longitude))
        serializer = StoreSerializer(closest_store)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Custom permissions: Only Admin can create, update, destroy; anyone can list/retrieve
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if request.user.role != 'ADMIN':
                self.permission_denied(request, message="Restricted to Admins only.")

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Expected data: address_id, store_id, items: [{product_id, quantity}]
        address_id = request.data.get('address_id')
        store_id = request.data.get('store_id')
        items_data = request.data.get('items', [])

        if not address_id or not store_id or not items_data:
            return Response({"error": "Missing checkout details."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            store_id=store_id,
            address_id=address_id,
            status='COMPLETED'
        )
        total = 0
        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            qty = item['quantity']
            if product.stock < qty:
                order.delete()
                return Response({"error": f"Insufficient stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)
            # Deduct stock
            product.stock -= qty
            product.save()
            price = product.price * qty
            total += price
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
        
        order.total_amount = total
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
