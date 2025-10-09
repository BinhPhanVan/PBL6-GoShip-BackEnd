from django.contrib import admin
from .models import Customer, Shipper, Admin
from django.utils.html import mark_safe
# Register your models here.


class ShipperCustom(admin.ModelAdmin):

    fieldsets = (
        ('Information', {
            'fields': ('account', 'name', 'avatar', 'gender', 'birth_date', 'home_address')
        }),
        ('Identification', {
            'fields': ('top_identification_image', 'back_identification_image', 'face_video'),
            'classes': ('collapse',),
        }),
        (None, {
            'fields': ('identification_info', 'confirmed')
        }),
    )
    list_display = ['account', 'name','avatar', 'gender', 'birth_date', 'confirmed']
    readonly_fields = ['account', 'avatar','top_identification_image',
                       'back_identification_image', 'face_video', 'identification_info']
    empty_value_display = '-empty-'
    list_filter = ("confirmed",)

    def top_identification_image(self, shipper):
        return mark_safe(
            '<img src="{url}" alt="Identification top" width="250" height="300">'
            .format(url=shipper.url_identification_top)
        )

    def back_identification_image(self, shipper):
        return mark_safe(
            '<img src="{url}" alt="Identification top" width="250" height="300">'
            .format(url=shipper.url_identification_back)
        )

    def face_video(self, shipper):
        return mark_safe(
            '<video width="320" height="240" controls><source src="{url}" type="video/mp4"></video>'
            .format(url=shipper.url_face_video)
        )

    def avatar(self, shipper):
        return mark_safe(
                    '<img src="{url}" alt="Avatar" width="150" height="150">'
                   .format(url=shipper.avatar_url)
                )

class CustomerCustom(admin.ModelAdmin):

    list_display = ['account', 'name','avatar', 'gender', 'birth_date', 'distance_view']
    fieldsets = (
        ('Information', {
            'fields': ('account', 'name','avatar', 'gender', 'birth_date', 'distance_view')
        }),
    )
    readonly_fields = ['account','avatar']
    
    def avatar(self, customer):
        return mark_safe(
                    '<img src="{url}" alt="Avatar" width="150" height="150">'
                   .format(url=customer.avatar_url)
                )


class AdminCustom(admin.ModelAdmin):

    list_display = ['account', 'name', 'gender', 'birth_date']

    readonly_fields = ['account']


admin.site.register(Customer, CustomerCustom)
admin.site.register(Shipper, ShipperCustom)
admin.site.register(Admin, AdminCustom)
