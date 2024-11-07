from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, GiftBox, Customer, Order, OrderItem
from .serializers import CategorySerializer, GiftBoxSerializer, OrderItemSerializer, CustomerSerializer
from django.contrib.sessions.models import Session
import json
import uuid
from .util import send_order_email
import base64
import os
from django.core.files.base import ContentFile
from datetime import datetime


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class GiftBoxListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        #categories = Category.objects.all()[:5]
        categorized_giftboxes = {}
        for category in categories:
            giftboxes = GiftBox.objects.filter(category=category)
            categorized_giftboxes[category.name] = GiftBoxSerializer(giftboxes, many=True).data
        return Response(categorized_giftboxes)
    
    def post(self, request):
        search_query = request.data.get('search_query')
        search_item = GiftBox.objects.filter(Q(name__icontains=search_query))[:5]
        searchItems = GiftBoxSerializer(search_item, many=True).data
        
        return Response(searchItems)

class GiftBoxDetailView(APIView):
    def get(self, request):
        giftbox = GiftBox.objects.all()
        serializer = GiftBoxSerializer(giftbox, many=True)
        return Response(serializer.data)


class AddToCartView(APIView):
    def post(self, request):
        response = Response("Added to cart succesfully")
        if 'anonymous_user_id' not in request.COOKIES:
            user_id = uuid.uuid4()
            response.set_cookie('anonymous_user_id', user_id, max_age=31536000)

        product_id = request.data.get('product_id')
        product_name = request.data.get('product_name')
        product_price = request.data.get('product_price')
        des_image = request.data.get('description_image')
        des_text = request.data.get('description_text')
        quantity = request.data.get('product_quantity')

        gift_box = GiftBox.objects.get(id=product_id)

        # Check if the user is authenticated and a customer
        if request.user.is_authenticated:
            customer = Customer.objects.get(email=request.user.email)
        else:
            #if not a customer use cookies to create an id
            shopper_id = request.COOKIES.get('anonymous_user_id')

            # Check if the non-customer shopper has shopped before
            existing_order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
            if existing_order:
                order = existing_order
            else:
                # Create a new order for the non-customer shopper
                order = Order.objects.create(session_id=shopper_id, cart_status='cart', total_price=0)
                order.save()
        #print(des_image, des_text, quantity)
        # Create a new order item
        if des_image == None and des_text == None and quantity == None:
            order_item = OrderItem.objects.create(order=order, gift_box=gift_box, quantity=1, price=gift_box.price)
        else:
            if des_image:
                # Decode the Base64 string
                format, imgstr = des_image.split(';base64,')  # Split the string to get the base64 part
                ext = format.split('/')[-1]  # Get the file extension
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
                # Create a unique filename
                dfilename = f"{product_name}_{current_time}.{ext}"
                image_data = ContentFile(base64.b64decode(imgstr), name=dfilename)  # Create a ContentFile
                #print(f"Received file: {des_image.name}, size: {des_image.size}")
                #print(des_image)
                order_item = OrderItem.objects.create(order=order, gift_box=gift_box, quantity=quantity, price=gift_box.price, description=des_text, image=image_data)
            else:
                order_item = OrderItem.objects.create(order=order, gift_box=gift_box, quantity=quantity, price=gift_box.price, description=des_text)
        
        order.save()
        return response

class CartItemsAPI(APIView):
    def get(self, request):
        shopper_id = request.COOKIES.get('anonymous_user_id')
        if request.user.is_authenticated:
            #order = Order.objects.get(email=request.user.email, cart_status='cart')
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
        else:
            #session = request.session
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()

        order_items = OrderItem.objects.filter(order=order)
        #Customer.objects.all().delete()
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        shopper_id = request.COOKIES.get('anonymous_user_id')
        order = Order.objects.get(session_id=shopper_id, cart_status='cart')
        order_id = request.data.get('order_id')
        cart_action = request.data.get('cart_action')
        orderItem = OrderItem.objects.get(id=order_id)
        try:
            int(cart_action)
            orderItem.quantity = cart_action
            orderItem.save()
            order.save()
        except ValueError:
            if cart_action == 'delete':
                orderItem.delete()
                order.save()

        return Response("Updated Successfully")

class CheckoutAPI(APIView):
    def get(self, request):
        # Get the order instance
        shopper_id = request.COOKIES.get('anonymous_user_id')
        if request.user.is_authenticated:
            #order = Order.objects.get(email=request.user.email, cart_status='cart')
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
        else:
            #session = request.session
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
        if order:
            # Check if the customer field is not null
            if order.customer:
                # If the customer field is not null, it means the person is a customer but doesn't have an account
                customer = order.customer
                #print(customer)
                serializer = CustomerSerializer(customer)
                response = Response(serializer.data)
            
            else:
                existing_customer = Customer.objects.filter(session_id=shopper_id).first()
        
                if existing_customer:
                    customer = existing_customer
                    order.customer = customer
                    order.save()
                        
                    #print(customer)
                    serializer = CustomerSerializer(customer)
                    response = Response(serializer.data)
                else:
                    response = Response({'message': "You have no billing record, please input below..."})
        else:
            existing_customer = Customer.objects.filter(session_id=shopper_id).first()
            if existing_customer:
                customer = existing_customer
                serializer = CustomerSerializer(customer)
                response = Response(serializer.data)
            else:
                response = Response({'message': "You have no billing record, please input below..."})

        return response


    def post(self, request):
        # Get the order instance

        shopper_id = request.COOKIES.get('anonymous_user_id')
        if request.user.is_authenticated:
            #order = Order.objects.get(email=request.user.email, cart_status='cart')
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
        else:
            #session = request.session
            order = Order.objects.filter(session_id=shopper_id, cart_status='cart').first()
        if order:
            # Check if the customer field is not null
            if order.customer:
                # If the customer field is not null, it means the person is a customer but doesn't have an account
                customer = order.customer
            else:
                # If the customer field is null, create a new customer instance
                customer = Customer.objects.create(
                    first_name=request.data.get('first_name'),
                    last_name=request.data.get('last_name'),
                    email=request.data.get('email'),
                    phone_number=request.data.get('phone_number'),
                    address=request.data.get('address'),
                    has_account=False,
                    session_id=shopper_id
                )
                customer.save()
                    
                order.customer = customer
                order.save()
            response = Response("done")
        else:
            response = Response("no order yet")
        return response

class PaymentSuccess(APIView):
    def post(self, request):
        action = request.data.get('actionn')
        receive_option = request.data.get('selected')
        if action == 'proceed':
            shopper_id = request.COOKIES.get('anonymous_user_id')
            if request.user.is_authenticated:
                #order = Order.objects.get(email=request.user.email, cart_status='cart')
                order = Order.objects.get(session_id=shopper_id, cart_status='cart')
            else:
                #session = request.session
                order = Order.objects.get(session_id=shopper_id, cart_status='cart')
            #order_items = OrderItem.objects.filter(order=order)
            #vendor_email = 'olehidavis@gmail.com'
            vendor_email = 'megzcrafts47@gmail.com'
            send_order_email(vendor_email, order, receive_option)
            # Update the cart status to 'real'
            order.cart_status = 'real'
            order.save()
            return Response({'status': 'success'})
        return Response({'status': 'failed'}, status=400)

class OrderView(APIView):
    def get(self, request):
        shopper_id = request.COOKIES.get('anonymous_user_id')
        if request.user.is_authenticated:
            #order = Order.objects.get(email=request.user.email, cart_status='cart')
            order = Order.objects.filter(session_id=shopper_id, cart_status='real')
        else:
            #session = request.session
            order = Order.objects.filter(session_id=shopper_id, cart_status='real')
    
        ordered = {}
        for orders in order:
            order_items = OrderItem.objects.filter(order=orders)
            ordered[orders.order_date.strftime('%Y-%m-%d %H:%M:%S')] = OrderItemSerializer(order_items, many=True).data
        return Response(ordered)
        
"""

def customer_account(request):
    customer = Customer.objects.get(user=request.user)
    orders = customer.order_set.all()
    return render(request, 'customer_account.html', {'customer': customer, 'orders': orders})

"""
"""
# views.py
from django.shortcuts import render, redirect
from .forms import CustomerAccountForm
from .models import Customer, CustomerAccount

def create_account(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        form = CustomerAccountForm(request.POST)
        if form.is_valid():
            customer_account = form.save(commit=False)
            customer_account.customer = customer
            customer_account.save()
            customer.has_account = True
            customer.save()
            return redirect('account_created')
    else:
        form = CustomerAccountForm()
    return render(request, 'create_account.html', {'form': form})

# views.py
def create_order(request):
    # ...
    customer = Customer.objects.get_or_create(email=request.user.email)[0]
    if customer.has_account:
        customer_account = customer.customeraccount
        # use account information to populate order details
    else:
        # create a new customer instance and proceed with order creation
    # ...

    def post(self, request):
    
        product_id = request.data.get('product_id')
        product_name = request.data.get('product_name')
        product_price = request.data.get('product_price')

        # Get the session user ID
        session_user_id = request.session.get('user_id')

        # If the user is authenticated, use their ID
        if request.user.is_authenticated:
            user_id = request.user.id
        # Otherwise, use the session user ID
        else:
            user_id = session_user_id

        cart = request.session.get('cart', {})
        if product_id in cart:
            cart[product_id]['quantity'] += 1
        else:
            cart[product_id] = {'name': product_name, 'price': product_price, 'quantity': 1}

        serializedCart = json.dumps(cart)
        request.session['cart'] = serializedCart
        print(request.session.get('cart'))
        request.session.modified = True
        #print(cart)
        return Response({"message": "Added to cart succesfully"})

"""