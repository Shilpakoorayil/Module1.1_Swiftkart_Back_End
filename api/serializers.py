from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Store, Address, Product, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile_number', 'role')

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        mobile_number = data.get('phone_number')
        otp = data.get('otp')

        if len(mobile_number) != 10 or not mobile_number.isdigit():
            raise serializers.ValidationError("Mobile number must be 10 digits.")
        if otp != "1234":
            raise serializers.ValidationError("Invalid OTP.")

        user, created = User.objects.get_or_create(
            mobile_number=mobile_number,
            defaults={'username': mobile_number, 'role': 'USER'}
        )
        return user

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        
        # Accept either explicitly set 'ADMIN' role, or Django superusers
        if user and (user.role == 'ADMIN' or user.is_superuser):
            # If they are a superuser but lacking the custom role, promote them so Product permissions pass
            if user.role != 'ADMIN':
                user.role = 'ADMIN'
                user.save(update_fields=['role'])
            return user
            
        raise serializers.ValidationError("Invalid Admin Credentials")


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user',)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'store', 'address', 'total_amount', 'status', 'created_at', 'items']
        read_only_fields = ('user', 'total_amount', 'status')
