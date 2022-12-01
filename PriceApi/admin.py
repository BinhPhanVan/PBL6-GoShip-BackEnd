from django.contrib import admin
from .models import Price
# Register your models here.

class PriceCustom(admin.ModelAdmin):
    list_display = ['id', 'initial_price','anchor','extra_price','price_percent','price_protect']
admin.site.register(Price,PriceCustom)


