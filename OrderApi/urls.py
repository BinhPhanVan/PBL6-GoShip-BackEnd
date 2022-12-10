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
    path('order/order-delivery/', OrderDelivery.as_view(), name='delivery_order'),
    path('order/request-confirm-done/', OrderRequestConfirmDone.as_view(), name='request_confirm_order'),
    path('order/confirm-done/', OrderConfirmDone.as_view(), name='confirm-done'),
    path('order/rate/', RatingOrder.as_view(), name='rating-order'),
]
urlpatterns += router.urls
