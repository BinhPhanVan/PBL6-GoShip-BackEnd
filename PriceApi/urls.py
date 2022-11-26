from django.urls import path
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from .views import *
app_name = "PriceApi"
router = routers.DefaultRouter()

urlpatterns = [
    path('distance/get_distance/', csrf_exempt(get_distance), name='get-distance'),
    path('distance/get_price/', csrf_exempt(get_price), name='get-price'),
]
urlpatterns += router.urls
