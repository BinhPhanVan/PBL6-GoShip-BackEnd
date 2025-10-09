from django.contrib import admin
from .models import Payment, Category, Status, Order
# Register your models here.


class OrderCustom(admin.ModelAdmin):
    list_display = ['id', 'customer', 'shipper', 'status']


class PaymentCustom(admin.ModelAdmin):
    list_display = ['id', 'type', 'description']


class CategoryCustom(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_protected']

class StatusCustom(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']

admin.site.register(Payment, PaymentCustom)
admin.site.register(Category, CategoryCustom)
admin.site.register(Status, StatusCustom)
admin.site.register(Order, OrderCustom)
