"""
URL configuration for ecom_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecom_app.urls')),  # Make sure 'ecom_app' is the correct app name
    path('store/', include('store.urls')),  # Make sure 'ecom_app' is the correct app name
    path('cart/', include('carts.urls')),

    #accounts
    path('accounts/', include('accounts.urls')),  # Make sure 'accounts' is the correct app name

    #Order path
    path('orders/', include('orders.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
