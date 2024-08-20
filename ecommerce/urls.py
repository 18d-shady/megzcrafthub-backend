from django.urls import path, include
from . import views
from .views import CategoryListView, GiftBoxListView, GiftBoxDetailView



urlpatterns = [
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/giftbox/', GiftBoxListView.as_view(), name='giftbox-list'),
    path('api/giftbox/product/', GiftBoxDetailView.as_view(), name='giftbox-detail'),
]

"""
path('products/', views.product_catalog, name='product_catalog'),
path('products/<int:product_id>/', views.product_detail, name='product_detail'),
path('account/', views.customer_account, name='customer_account'),
path('orders/create/', views.create_order, name='create_order'),
path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
"""