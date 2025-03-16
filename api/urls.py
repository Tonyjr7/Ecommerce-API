from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

# Import views from api.views module
from api.views import (CreateCategoryView, CategoryDetailView, ProductListView, CreateProductView, 
                       ProductDetailView, UpdateProductView, CategoryListView, ProductByCategoryView,
                       UserSignupView, UserListView, UserLogoutView, AddCartItemView, ListCartItemsView,
                        RemoveCartItemView, CheckoutView, CheckoutOrderView, RemoveOrderView,
                        create_payment, verify_payment)

urlpatterns = [
    path("payments/initiate/", create_payment, name="initiate-payment"),
    path("payments/verify", verify_payment, name="paystack-webhook"),
    # URL for category
    path('admin/categories/', CreateCategoryView.as_view(), name="create_category"),
    path('admin/category/<int:pk>', CategoryDetailView.as_view(), name="category_detail"),
    # URL for product admin
    path('admin/add-product/', CreateProductView.as_view(), name="add_product"),
    path('admin/product/update/<int:pk>', UpdateProductView.as_view(), name="update_product"),
    # URL for product list
    path('products', ProductListView.as_view(), name="product_list"),
    path('product/<int:pk>', ProductDetailView.as_view(), name="product_detail"),
    # URL for category product list by user
    path('categories/', CategoryListView.as_view(), name="categories"),
    path('category/<int:category_id>/products', ProductByCategoryView.as_view(), name="products_by_category"),
    # URL for authentications
    path('auth/register/', UserSignupView.as_view(), name="user_signup"),
    path('auth/login/', obtain_auth_token, name="user_login"),
    path('auth/logout/', UserLogoutView.as_view(), name="user_logout"),
    # URL for user list
    path('admin/users/', UserListView.as_view(), name="user_list"),  
    # URL for add cart item
    path('cart/add/', AddCartItemView.as_view(), name="add_cart_item"),
    # URL for list cart items
    path('cart/items/', ListCartItemsView.as_view(), name="list_cart_items"),
    # URL for remove cart item
    path('cart/item/remove/', RemoveCartItemView.as_view(), name="remove_cart_item"),
    # URL for checkout
    path('cart/checkout/', CheckoutView.as_view(), name="checkout"),
    # URL for remove order
    path('order/remove/', RemoveOrderView.as_view(), name="remove_order"),  # URL for checkout order
    # URL for checkout order
    path('admin/orders/', CheckoutOrderView.as_view(), name="checkout_order")
]