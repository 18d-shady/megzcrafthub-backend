from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class GiftBoxSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = GiftBox
        fields = ['id', 'name', 'description', 'price', 'image', 'category']

"""
class GiftBoxCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    giftbox = GiftBoxSerializer()
    class Meta:
        model = GiftBoxCategory
        fields = ['id', 'category', 'giftbox']
"""

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'has_account']

class CustomerAccountSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    class Meta:
        model = CustomerAccount
        fields = ['id', 'username', 'password']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    gift_box = GiftBoxSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'order_date', 'total_price']

class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    gift_box = GiftBoxSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'gift_box', 'quantity', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_method', 'payment_date', 'amount']