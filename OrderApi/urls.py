from django.urls import path
from rest_framework import routers
from .views import *
app_name = "OrderApi"
router = routers.DefaultRouter()
router.register(r'payment', PaymentView, basename='payment')
router.register(r'category', CategoryView, basename='category')
router.register(r'status', StatusView, basename='status')

urlpatterns = [
    path('order/', OrderView.as_view(), name='order'),
    path('user/get-history-order/', HistoryOrderView.as_view(), name='history_order'),
]
urlpatterns += router.urls
