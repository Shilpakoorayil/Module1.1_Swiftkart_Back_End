from django.contrib import admin
from .models import User, Store, Address, Product, Order, OrderItem

admin.site.register(User)
admin.site.register(Store)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
