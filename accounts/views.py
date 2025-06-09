from django.shortcuts import render, redirect
import requests
from urllib.parse import urlparse, parse_qs

from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import Account
from carts.models import Cart, CartItem  # Add this import for Cart and CartItem models
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from carts.views import _cart_id  # Import _cart_id function if defined in carts/views.py

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            #user activation 
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,  # FIXED
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),  # FIXED
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Activation link has send in your email.')

            return redirect('/accounts/login/?command=verification&email='+email)  # Redirect to home page after successful registration
#j1hno@doe33
    else:
        form = RegisterForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    # Store variations from the current cart
                    product_variation = []
                    for item in cart_items:
                        variation = item.variation.all()
                        product_variation.append(list(variation))

                    # Get user cart items
                    user_cart_items = CartItem.objects.filter(user=user)
                    existing_var_list = []
                    item_ids = []

                    for item in user_cart_items:
                        existing_var = item.variation.all()
                        existing_var_list.append(list(existing_var))
                        item_ids.append(item.id)

                    # Check if variation already exists in user cart
                    for pr in product_variation:
                        if pr in existing_var_list:
                            index = existing_var_list.index(pr)
                            item_id = item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.save()
                        else:
                            # Assign cart item to the user
                            for item in cart_items:
                                item.user = user
                                item.save()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, 'Login successful.')
            url = request.META.get('HTTP_REFERER')  # Get the previous page URL
            try:
                query = urlparse(url).query
                params = parse_qs(query)
                if 'next' in params:
                    next_page = params['next'][0]  # get the first value of 'next'
                    return redirect(next_page)
            except:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'accounts/login.html')
 

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')  # Redirect to login page after logout

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password token generation
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired!')
        return redirect('login')
def resetPassword(request):
    if request.method == "POST":
        password = request.POST.get('password')  # fixed
        confirm_password = request.POST.get('confirm_password')  # fixed

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has  reset successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
