from django.contrib import admin
from .models import Order, Payment, OrderProduct



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'first_name', 'email', 'phone', 'order_total', 'status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email')
    list_filter = ('status', 'is_ordered', 'created_at')
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
