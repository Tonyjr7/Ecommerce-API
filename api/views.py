# imports from project
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
import requests
from rest_framework.decorators import api_view
import base64
from django.utils.crypto import get_random_string
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from api.email_service import email_service

# imports from api
from api.serializers import (CategorySerializer, ProductSerializer, UserRegistrationSerializer,
                            CartItemSerializer, CartSerializer, OrderSerializer)
from api.models import Category, Product, CartItem, Cart, Orders, Payment
    
# categories views('POST', 'GET')
class CreateCategoryView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()
        return serializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        category = self.kwargs['pk']
        return Category.objects.filter(id=category)

    def perform_update(self, serializer):
        serializer.save()
        return serializer.instance
    
    def perform_delete(self, serializer):
        serializer.delete()
        return serializer
    
# product admin
class CreateProductView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()
        return serializer
    
class UpdateProductView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        product = self.kwargs['pk']
        return Product.objects.filter(id=product)
    
    def perform_update(self, serializer):
        serializer.save()
        return serializer.instance
    
    def perform_delete(self, serializer):
        serializer.delete()
        return serializer
    
# user product views
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        product = self.kwargs['pk']
        return Product.objects.filter(id=product)

# category product list for user 
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.prefetch_related('products').all()
    serializer_class = CategorySerializer

class ProductByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category_id=category_id)
    
class UserSignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if username is None or password is None:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = User.objects.create_user(username=username, email=email,
                                        password=password, first_name=first_name, last_name=last_name)
        token = Token.objects.create(user=user)

        return Response({'success': 'User created successfully.', 'token': token.key}, status=status.HTTP_201_CREATED)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail':'Logout Successful.'},status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail':'Error Logging Out'},status=status.HTTP_200_OK)
    
# admin can view users
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdminUser]

class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        #check if cart exists or create
        cart, cart_created = Cart.objects.get_or_create(user=request.user)

        if int(quantity) >= product.quantity:
            return Response({'error': 'Quantity exceeds available stock.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # update product quantity
        product.quantity -= int(quantity)
        product.save()

        # check if product is already in cart
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += int(quantity)
            cart_price = product.price * int(quantity)
            cart_item.price += cart_price
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.price = product.price * int(quantity)
            cart_item.save()

        cart.total_price = sum(item.price for item in cart.items.all())
        cart.save()

        return Response({'detail': 'Item added to cart.'}, status=status.HTTP_201_CREATED)

class ListCartItemsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cartitem_quantity = request.data.get('quantity')
        cartitem_id = request.data.get('item')

        if not cartitem_id or not cartitem_quantity:
            return Response({'error': 'CartItem ID and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cartitem = CartItem.objects.get(id=cartitem_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart = cartitem.cart
        product = cartitem.product
        p = Product.objects.get(name=product.name)
        print(p)
        quantity_to_remove = int(cartitem_quantity)
        deduct_price = product.price * Decimal(quantity_to_remove)

        if quantity_to_remove > cartitem.quantity:
            return Response({'error': 'Not enough quantity in cart item.'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart.total_price -= deduct_price

        if quantity_to_remove == cartitem.quantity:
            cartitem.delete()
            message = 'Item deleted from cart.'
        else:
            cartitem.quantity -= quantity_to_remove
            cartitem.price -= deduct_price
            cartitem.save()
            message = 'Item quantity updated.'

        cart.save()
        return Response({'detail': message}, status=status.HTTP_200_OK)
    
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        shipping_address = request.data.get('shipping_address')
        phone_number = request.data.get('phone_number')

        user = request.user

        if not shipping_address or not phone_number:
            return Response({'error': 'Shipping address and phone number are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart not found'})
        try:
            order = Orders.objects.create(user=user, 
                                          cart=cart, shipping_address=shipping_address, 
                                          total_price=cart.total_price, phone=phone_number)
            
            email_service.send_order_email(user.email, user.username, order.order_number, order.total_price)
            
            #update product quantity
            for item in cart.items.all():
                product_id = item.product.id
                product_order_quantity = item.quantity
                product = Product.objects.get(id=product_id)

                if product.quantity < product_order_quantity:
                    return Response({'detail': f"Not enough stock for {product.name}"})
                else:
                    product.quantity -= product_order_quantity
                    product.save()

        except Exception as e:
            return Response({'detail': f'Error creating order: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Order placed successfully': order.order_number })
    
    def get(self, request):
        try:
            order = Orders.objects.get(user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Orders.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class RemoveOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_number = request.data.get('order_number')

        if not order_number:
            return Response({'error': 'Order ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Orders.objects.get(order_number=order_number)
            cart = Cart.objects.get(id=order.cart.id)
            cartitems = CartItem.objects.filter(cart=cart)

            if order.order_status == 'PENDING':
                # Efficiently handle products and quantities
                for item in cartitems:
                    product = item.product
                    product.quantity += item.quantity
                    product.save()

                # Delete all items after processing
                cartitems.delete()
                cart.delete()

                # Cancel the order
                order.order_status = 'CANCELLED'
                order.save()

                return Response({'detail': 'Order cancelled successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Cannot cancel an order that is already shipped or delivered.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Orders.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)


class CheckoutOrderView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            orders = Orders.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Orders.DoesNotExist:
            return Response({'detail': 'No orders found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        order_number = request.data.get('order_number')
        order_status = request.data.get('status')
        
        if not order_number:
            return Response({'error': 'Order number and status are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Orders.objects.get(order_number=order_number)
            order.order_status = order_status
            order.save()
            return Response({'detail': 'Order status updated successfully.'}, status=status.HTTP_200_OK)
        except Orders.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
def create_payment(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
        order = Orders.objects.get(cart=cart)
    except (Cart.DoesNotExist, Orders.DoesNotExist):
        return Response({'detail': 'User does not have an active cart or order'}, status=400)
    
    amount = order.total_price
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'email': user.email,
        'amount': int(amount * 100),  # Paystack accepts amount in kobo
        'callback_url': 'http://localhost:8000/api/v1/payments/verify/',  # Adjust for production
    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status']:
        # Create payment record
        Payment.objects.create(
            user=request.user,
            amount=amount,
            order_id=order.order_number,
            reference=response_data['data']['reference'],
            status='pending'
        )
        return Response({'authorization_url': response_data['data']['authorization_url']})
    
    return Response({'error': 'Failed to initialize payment'}, status=400)

@api_view(['GET'])
def verify_payment(request):
    reference = request.GET.get('reference')
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()

    # Verify the payment status
    if response_data['status'] and response_data['data']['status'] == 'success':
        try:
            # Retrieve the payment using the reference
            payment = Payment.objects.get(reference=reference)

            # Mark the payment as successful
            payment.status = 'success'
            payment.save()

            # Retrieve the associated order
            order = Orders.objects.get(order_number=payment.order_id)
            order.order_status = 'PAID'
            order.save()

            # Delete the cart associated with the payment (if applicable)
            cart = Cart.objects.get(user=payment.user)
            cart.delete()

            return Response({'status': 'Payment successful'})

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        except Orders.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

    return Response({'status': 'Payment failed'}, status=400)