from django.contrib import admin
from .models import Account
from UserApi.models import *
# Register your models here.


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name', 'role')
    list_filter = ("role",)
    fieldsets = (
        ('Information', {
            'fields': ('phone_number', 'password','token_device')
        }),

        ('Authorization', {
            'fields': ('is_staff', 'is_superuser','is_active','role')
        }),
    )
    def name(self, obj):
        res = []
        if obj.role == 1:
            res.append(Customer.objects.filter(account=obj).first())
        elif obj.role == 2:
            res.append(Shipper.objects.filter(account=obj).first())
        else:
            res.append(Admin.objects.filter(account=obj).first())
        return res

