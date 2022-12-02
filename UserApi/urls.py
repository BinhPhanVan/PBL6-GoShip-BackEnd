from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.decorators.csrf import csrf_exempt
from .views import *
app_name = "UserApi"
router = routers.DefaultRouter()
router.register(r'user/register', RegisterViewSet, basename='user/register')

urlpatterns = [
    path('api/token/', csrf_exempt(MyTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),

    path("shipper/confirm-shipper/", ConfirmShipper.as_view(), name="confirm"),
    path("shipper/detail/", ShipperViewSet.as_view(), name="shipper-detail"),
    path("shipper/update/", ShipperUpdateSerializer.as_view(), name="shipper-update"),
    
    path("customer/detail/", CustomerViewSet.as_view(), name="customer-detail"),
    
    path("user/login/",csrf_exempt(LoginView.as_view()), name="login"),
    path("user/change-password/", ChangePassword.as_view(), name="change-password"),
    path("user/logout/", Logout.as_view(), name="logout"),
    path("user/update-device-token/", UpdateDeviceTokenView.as_view(), name="update-device-token"),
    path("user/get-info/", UserDetailView.as_view(), name="get-info")
]
urlpatterns += router.urls
