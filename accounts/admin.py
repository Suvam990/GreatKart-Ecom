from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')

    readonly_fields=('last_login', 'date_joined')
    ordering=('-date_joined',)
    readonly_fields = ('password', 'last_login', 'date_joined')  
    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff', 'is_superadmin')}),
        ('Important Dates', {'fields': ('last_login',)}),  
    )

admin.site.register(Account, AccountAdmin)
