from django.urls import path
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from .views import *
app_name = "OrderApi"
router = routers.DefaultRouter()
router.register(r'payment', PaymentView, basename='payment')
router.register(r'category', CategoryView, basename='category')
router.register(r'status', StatusView, basename='status')

urlpatterns = [
    path('order/', OrderView.as_view(), name='order'),
    path('order/order-detail/<int:order_id>/', OrderDetailView.as_view(), name='detail_order'),
    path('order/order-receive/', OrderReceiveView.as_view(), name='receive_order'),
]
urlpatterns += router.urls
