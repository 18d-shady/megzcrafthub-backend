from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, GiftBox, Customer, Order
from .serializers import CategorySerializer, GiftBoxSerializer


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
            giftboxes = GiftBox.objects.filter(category=category)[:5]
            categorized_giftboxes[category.name] = GiftBoxSerializer(giftboxes, many=True).data
        return Response(categorized_giftboxes)

class GiftBoxDetailView(APIView):
    def get(self, request):
        giftbox = GiftBox.objects.all()
        serializer = GiftBoxSerializer(giftbox, many=True)
        return Response(serializer.data)

# Create your views here.
"""
def product_catalog(request):
    products = Product.objects.all()
    return render(request, 'product_catalog.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def customer_account(request):
    customer = Customer.objects.get(user=request.user)
    orders = customer.order_set.all()
    return render(request, 'customer_account.html', {'customer': customer, 'orders': orders})

def create_order(request):
    if request.method == 'POST':
        # create a new order
        pass
    return render(request, 'create_order.html')

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_detail.html', {'order': order})
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
"""