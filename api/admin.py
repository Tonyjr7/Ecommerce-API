from django.contrib import admin
from api.models import Product, Category, User, Cart, CartItem, Orders, Payment

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Orders)

admin.site.register(Payment)


# Register your models here.
