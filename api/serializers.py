from rest_framework import serializers
from api.models import Category, Product, Cart, CartItem, Orders
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(required=True)
    class Meta:
        model = Product
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = "__all__"
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input-type':'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'is_staff']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class OrderSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer(many=False, read_only=True)
    cart = CartSerializer(many=False, read_only=True)
    class Meta:
        model = Orders 
        fields = '__all__'


