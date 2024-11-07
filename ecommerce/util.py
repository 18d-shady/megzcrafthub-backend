from .models import GiftBox, Customer, Order, OrderItem
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_email(vendor_email, order, receive_option):
    subject = 'New Order Received'
    
    # Get the order items associated with the order
    order_items = OrderItem.objects.filter(order=order)
    
    # Prepare data for the email template
    order_details = []
    for item in order_items:
        gift_box = GiftBox.objects.get(id=item.gift_box.id)  # Assuming gift_box is a ForeignKey in OrderItem
        order_details.append({
            'gift_box_name': gift_box.name,
            'gift_box_image': gift_box.image.url if gift_box.image else None,  # Get the image URL
            'item_description_image': item.image.url if item.image else None,  # Get the description image URL
            'quantity': item.quantity,
            'price': item.price,
            'description': item.description,
        })

    # Get customer information
    customer = Customer.objects.get(id=order.customer.id)  # Assuming customer is a ForeignKey in Order
    customer_info = {
        'fname': customer.first_name,
        'lname': customer.last_name,
        'email': customer.email,
        'phone_number': customer.phone_number,
        'address': customer.address,
    }

    if receive_option == 'option2':
        receive_option = "Pickup"
    else:
        receive_option = "Delivery"
    

    # Render the email template
    html_message = render_to_string('order_email_template.html', {
        'total_price': order.total_price,
        'order_details': order_details,
        'customer_info': customer_info,
        'receive_option': receive_option,
    })
    plain_message = strip_tags(html_message)
    
    #print(plain_message)  # For debugging
    from_email = 'megzcrafthubsourcemail@gmail.com'

    # Send the email
    send_mail(subject, plain_message, from_email, [vendor_email], html_message=html_message)