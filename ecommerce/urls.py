from django.urls import path, include
from . import views
from .views import CategoryListView, GiftBoxListView, GiftBoxDetailView



urlpatterns = [
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/giftbox/', GiftBoxListView.as_view(), name='giftbox-list'),
    path('api/giftbox/product/', GiftBoxDetailView.as_view(), name='giftbox-detail'),
    path('api/add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('api/view-cart/', views.CartItemsAPI.as_view(), name='view_cart'),
    path('api/order/', views.CheckoutAPI.as_view(), name='order'),
    path('api/final-order/', views.OrderView.as_view(), name='real_order'),
    path('api/complete-checkout/', views.PaymentSuccess.as_view(), name='finish_order'),
    #path('api/view-cart/<int:pk>/', views.CartItemsAPI.as_view(), name='view_cart'),
]


"""
path('products/', views.product_catalog, name='product_catalog'),
path('products/<int:product_id>/', views.product_detail, name='product_detail'),
path('account/', views.customer_account, name='customer_account'),
path('orders/create/', views.create_order, name='create_order'),
path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
"""