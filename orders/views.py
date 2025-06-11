from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product  # Add this import for Product model
from django.template.loader import render_to_string  # Import for render_to_string
from django.core.mail import EmailMessage  # Import for sending emails
from django.http import JsonResponse  # Import for returning JSON responses
import datetime
import json




def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    #store tranaction details inside payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )

   
    payment.save()
    order.payment = payment
    order.is_ordered=True
    order.save()


    #move the cart itmes to order prioduct table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = payment  # ✅ Correct: assign payment to the orderproduct
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # Save product variations (if any)
        product_variation = item.variation.all()
        orderproduct.variation.set(product_variation)



    #reduce the item/quantity of the sold products
        product = item.product
        product.stock -= item.quantity
        product.save()

    #cart cleare
    cart_items = CartItem.objects.filter(user=request.user)
    cart_items.delete()


    #send order recived email to customer
    mail_subject = 'Thankyou for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order':order
                
            })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = "html"
    send_email.send()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }
    return JsonResponse(data)
    # return render(request, 'orders/payments.html')








def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')  # spelling fix

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (2 * total) / 100  # 2% tax example
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Get real IP address
            # ip = request.META.get('HTTP_X_FORWARDED_FOR')
            # if ip:
            #     ip = ip.split(',')[0].strip()
            # else:
            #     ip = request.META.get('REMOTE_ADDR')
            # data.ip = ip

            # data.save()

            today = datetime.date.today()
            current_date = today.strftime("%y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered = False, order_number=order_number)

            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }

            return render(request, 'orders/payments.html', context)


    else:
        return redirect('checkout')
        
def order_complate(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment':payment,
            'subtotal':subtotal

        }
        return render(request, 'orders/order_complate.html', context)
    
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')