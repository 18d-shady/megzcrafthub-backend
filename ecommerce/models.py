from django.db import models
#from django.contrib.auth.models import AbstractUser

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class GiftBox(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='giftbox_images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


"""
class GiftBoxCategory(models.Model):
    gift_box = models.ForeignKey(GiftBox, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)    
"""

class CustomerAccount(models.Model):
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    """
    def get_order_history(self):
        return self.order_set.all()
    """

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_account = models.BooleanField(default=False)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    

class Order(models.Model):
	#user = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cart_status = models.CharField(max_length=20, choices=[
        ('cart', 'Cart'),
        ('real', 'Real'),
    ], default='cart')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    session_id = models.CharField(max_length=255, null=True, blank=True)

    
    def save(self, *args, **kwargs):
        # Only calculate total_price if the instance already has a primary key
        if self.pk is not None:
            self.total_price = sum(item.price * item.quantity for item in self.orderitem_set.all())
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    gift_box = models.ForeignKey(GiftBox, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)  # Text description
    image = models.ImageField(upload_to='order_item_images/', blank=True)        
    
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer')
    ])
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)   



