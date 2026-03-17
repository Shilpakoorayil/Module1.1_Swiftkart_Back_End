from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Store, Product, Address, Order

class SwiftKartAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create Admin
        self.admin = User.objects.create_user(username='admin', password='admin123', role='ADMIN')
        # Create Stores
        self.store1 = Store.objects.create(name='Koramangala Dark Store', latitude=12.9352, longitude=77.6245)
        self.store2 = Store.objects.create(name='Indiranagar Dark Store', latitude=12.9784, longitude=77.6408)
        # Create Product
        self.product = Product.objects.create(name='Milk', price=25.0, stock=50)

    def test_user_login(self):
        url = reverse('user-login')
        data = {'mobile_number': '9876543210', 'otp': '1234'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['role'], 'USER')

    def test_admin_login(self):
        url = reverse('admin-login')
        data = {'username': 'admin', 'password': 'admin123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_guest_login(self):
        url = reverse('guest-login')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'GUEST')

    def test_closest_store(self):
        url = reverse('closest-store')
        data = {'latitude': 12.9716, 'longitude': 77.5946} # Bangalore center, closer to Indiranagar
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 12.9784/77.6408 is closer to 12.9716/77.5946 than Koramangala
        self.assertEqual(response.data['name'], 'Indiranagar Dark Store')

    def test_product_crud_permissions(self):
        # Unauthenticated user trying to create product
        url = reverse('product-list')
        data = {'name': 'Bread', 'price': 30.0, 'stock': 20}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated regular user trying to create product
        self.client.force_authenticate(user=User.objects.create_user(username='test', role='USER'))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin trying to create product
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_checkout_flow(self):
        user = User.objects.create_user(username='buyer', role='USER')
        self.client.force_authenticate(user=user)
        
        address = Address.objects.create(user=user, street="123 Main St", latitude=12.9, longitude=77.6)
        
        url = reverse('checkout')
        data = {
            'address_id': address.id,
            'store_id': self.store1.id,
            'items': [{'product_id': self.product.id, 'quantity': 2}]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_amount'], '50.00')
        
        # Verify stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 48)
