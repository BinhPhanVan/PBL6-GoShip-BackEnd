from django.contrib import admin
from .models import Notification
# Register your models here.

class NotificationCustom(admin.ModelAdmin):
    list_display = ['id', 'title', 'body']

admin.site.register(Notification,NotificationCustom)