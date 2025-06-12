from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import  Product
from .models import Category
from .models import ReviewRating
from orders.models import OrderProduct
from .forms import ReviewForm
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.contrib import messages
# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products =None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(products, 2)
        page = request.GET.get("page")
        page_products = paginator.get_page(page)
        product_count = products.count()
    else:

        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 4)
        page = request.GET.get("page")
        page_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products':page_products,
        'product_count':product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug=product_slug)

        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()

    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct =OrderProduct.objects.filter(user = request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    #get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    context ={
        'single_product':single_product,
        "in_cart": in_cart,
        'orderproduct' : orderproduct,
        'reviews':reviews
    }
    for product in Product.objects.all():
     print(product.get_url())


    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            from django.db.models import Q
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
        
    }
    return render(request, 'store/store.html',       context=context) 

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user_id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user = request.user
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
        return redirect(url)


# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q
# from .models import Product, Category, ReviewRating
# from .forms import ReviewForm
# from carts.models import CartItem
# from carts.views import _cart_id
# from django.core.paginator import Paginator
# from django.http import HttpResponse
# from django.contrib import messages
# from django.urls import reverse

# def store(request, category_slug=None):
#     categories = None
#     products = None

#     if category_slug:
#         categories = get_object_or_404(Category, slug=category_slug)
#         products = Product.objects.filter(category=categories, is_available=True)
#         paginator = Paginator(products, 2)
#     else:
#         products = Product.objects.filter(is_available=True).order_by('id')
#         paginator = Paginator(products, 4)

#     page = request.GET.get("page")
#     page_products = paginator.get_page(page)
#     product_count = products.count()

#     context = {
#         'products': page_products,
#         'product_count': product_count,
#     }
#     return render(request, 'store/store.html', context)


# def product_detail(request, category_slug, product_slug):
#     single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
#     in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

#     context = {
#         'single_product': single_product,
#         'in_cart': in_cart,
#     }

#     return render(request, 'store/product_detail.html', context)


# def search(request):
#     products = []
#     product_count = 0

#     if 'keyword' in request.GET:
#         keyword = request.GET['keyword']
#         if keyword:
#             products = Product.objects.order_by('-created_date').filter(
#                 Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
#             )
#             product_count = products.count()

#     context = {
#         'products': products,
#         'product_count': product_count,
#     }
#     return render(request, 'store/store.html', context)


# def submit_review(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if request.method == "POST":
#         try:
#             reviews = ReviewRating.objects.get(user_id=request.user.id, product=product)
#             form = ReviewForm(request.POST, instance=reviews)
#             form.save()
#             messages.success(request, 'Thank you! Your review has been updated.')
#         except ReviewRating.DoesNotExist:
#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.subject = form.cleaned_data['subject']
#                 data.rating = form.cleaned_data['rating']
#                 data.review = form.cleaned_data['review']
#                 data.ip = request.META.get('REMOTE_ADDR')
#                 data.product = product
#                 data.user = request.user
#                 data.save()
#                 messages.success(request, "Thank you! Your review has been submitted.")

#     # Redirect to the correct product detail page
#     url = reverse('product_detail', args=[product.category.slug, product.slug])
#     return redirect(url)
