from rest_framework import generics, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from BaseApi.permissions import *
from .models import Account, Address, Shipper, Customer
from OrderApi.models import Order
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from rest_framework.generics import GenericAPIView
from OrderApi.models import Rate
from datetime import datetime
from django.db.models import Avg
from statistics import mean
from OrderApi.serializers import RateSerializer
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Account.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        if not Account.objects.filter(phone_number=request.data.get('phone_number')).exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            account = serializer.save()
            authenticate(
                request,
                username=request.data.get('phone_number'),
                password=request.data.get('password')
            )
            refresh = MyTokenObtainPairSerializer.get_token(account)
            response = {
                "status": "success",
                "data": {
                    'role': account.role,
                    'phone_number': account.phone_number,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    "detail": "Đăng ký thành công!"
                },
                "detail": None
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)

        return Response(
            {
                "status": "error",
                "data": None,
                "detail": "Tài khoản đã tồn tại!"
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            logout(request)
            account = authenticate(
                request,
                username=serializer.validated_data['phone_number'],
                password=serializer.validated_data['password']
            )
            if account:
                refresh = MyTokenObtainPairSerializer.get_token(account)
                print(account)
                data = {
                    'phone_number': RegisterSerializer(account).data['phone_number'],
                    'role': RegisterSerializer(account).data['role'],
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    'detail': "Đăng nhập thành công !"
                }
                response = {
                    "status": "success",
                    "data": data,
                    "detail": None
                }
                return Response(response, status=status.HTTP_200_OK)

        response = {
            "status": "error",
            "data": None,
            "detail": "Tài khoản không hợp lệ!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        logout(request)
        response = {
            "status": "success",
            "data": None,
            "detail": None
        }
        return Response(response, status=status.HTTP_204_NO_CONTENT)


class ConfirmShipper(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = ConfirmShipperSerializer

    def patch(self, request):
        response = {
                "status": "error",
                "data": None,
                "detail": "Tài khoản không hợp lệ!"
            }
        try:
            account = Account.objects.filter(
                phone_number=request.user.phone_number)
            if account.exists():
                data_info = request.data.get(
                    'identification_info')
                info = data_info.split('|')   
                birth_date =datetime(day=int(info[3][:2]), month=int(info[3][2:4]), year=int(info[3][4:]))
                home_address = info[5]
                shipper = Shipper.objects.filter(
                    account__phone_number=request.user.phone_number)
                shipper.update(gender=request.data.get('gender'),
                            name=request.data.get('name'),
                            address=Address.objects.create(
                                **request.data.get('address')),
                            url_identification_top=request.data.get(
                                'url_identification_top'),
                            url_identification_back=request.data.get(
                                'url_identification_back'),
                            identification_info=data_info,
                            url_face_video=request.data.get('url_face_video'),
                            confirmed=1,
                            birth_date=birth_date,
                            home_address=home_address
                            )
                response = {
                    "status": "success",
                    "data": ShipperSerializer(shipper.first()).data,
                    "detail": None
                }
                return Response(response, status=status.HTTP_200_OK)
        except:
            response["detail"] = "Căn cước công dân không hợp lệ!"
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class ShipperViewSet(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = ShipperSerializer

    def get(self, request):
        shipper = Shipper.objects.filter(
            account__phone_number=request.user.phone_number)
        if shipper.exists():
            response = {
                "status": "success",
                "data": ShipperSerializer(shipper.first()).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class ShipperUpdateSerializer(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = ShipperUpdateSerializer

    def put(self, request):
        shipper = Shipper.objects.get(
            account__phone_number=request.user.phone_number)
        shipper.distance_receive = request.data.get('distance_receive')
        shipper.avatar_url = request.data.get('avatar_url')
        shipper.save()
        response = {
            "status": "success",
            "data": ShipperSerializer(shipper).data,
            "detail": None
        }
        return Response(response, status=status.HTTP_200_OK)


class CustomerViewSet(GenericAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsCustomerPermission]
    serializer_class = CustomerSerializer

    def get(self, request):
        customer = Customer.objects.filter(
            account__phone_number=request.user.phone_number)
        if customer.exists():
            response = {
                "status": "success",
                "data": CustomerSerializer(customer.first()).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

    def put(self, request):
        customer = Customer.objects.filter(
            account__phone_number=request.user.phone_number)
        address = request.data.get('address')
        if customer.exists():
            if customer.first().address is None:
                address = Address.objects.create(**request.data.get('address'))
                customer.update(address=address)
            else:
                Address.objects.filter(id=customer.first().address.id).update(
                    address_notes=address.get('address_notes'),
                    latitude=address.get('latitude'),
                    longitude=address.get('longitude'),
                )
            customer.update(
                name=request.data.get('name'),
                gender=request.data.get('gender'),
                avatar_url=request.data.get('avatar_url'),
                distance_view=request.data.get('distance_view'),
                birth_date=request.data.get('birth_date'),
            )
            response = {
                "status": "success",
                "data": CustomerSerializer(customer.first()).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class UpdateDeviceTokenView(GenericAPIView):
    serializer_class = UpdateDeviceToken
    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        token_device = request.data.get('token_device')
        account = Account.objects.filter(
            phone_number=request.user.phone_number)
        print(request.user.phone_number)

        if account.exists():
            account.update(token_device=token_device)
            response = {
                "status": "success",
                "data": None,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(
            data=response,
            status=status.HTTp_400_BAD_REQUEST)


def check_pass(password):
    if len(password) < 6:
        return False
    return True


def same_pass(new_password, repeat_password):
    if new_password != repeat_password:
        return False
    return True


class ChangePassword(GenericAPIView):
    serializer_class = ChangePassWordSerializer
    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = ChangePassWordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")
            repeat_password = request.data.get("repeat_password")
            if request.user.check_password(old_password):
                if check_pass(new_password):
                    if same_pass(new_password, repeat_password):
                        request.user.set_password(new_password)
                        request.user.save()
                        response = {
                            "status": "success",
                            "data": None,
                            "detail": None
                        }
                        return Response(response, status=status.HTTP_201_CREATED)
                    else:
                        message = "Mật khẩu không khớp nhau!"
                else:
                    message = "Mật khẩu tối thiểu 8 ký tự!"
            else:
                message = "Mật khẩu cũ không đúng"
        else:
            message = "Dữ liệu không hợp lệ!"
        response = {
            "status": "error",
            "data": None,
            "detail": message
        }
        return Response(response,
                        status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    serializer_class = PhoneNumberSerializer
    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('phone_number',in_= openapi.IN_QUERY,description='phone_number',type=openapi.TYPE_STRING)])
    def get(self, request, *args, **kwargs):
        phone_number = request.query_params.get('phone_number')
        account = Account.objects.filter(phone_number=phone_number)
        if account.exists():
            if account.first().role == 1:
                customer = Customer.objects.filter(
                    account__phone_number=account.first().phone_number)
                response = {
                    "status": "success",
                    "data": DetailCustomerSerializer(customer.first()).data,
                    "detail": None
                }
                return Response(response, status=status.HTTP_202_ACCEPTED)
            elif account.first().role == 2:
                shipper = Shipper.objects.filter(
                    account__phone_number=account.first().phone_number)
                response = {
                    "status": "success",
                    "data": DetailShipperSerializer(shipper.first()).data,
                    "detail": None
                }
                return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status": "error",
            "data": None,
            "detail": "Số điện thoại không hợp lệ!"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class RatingShipper(GenericAPIView):
    queryset = Rate.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RateSerializer

    def get(self, request, shipper_id):
        orders = list(Order.objects.filter(shipper_id=shipper_id))
        list_point = []
        for order in orders:
            if order.rate: list_point.append(order.rate.rate)
        response = {
            "status": "success",
            "data": mean(list_point) if len(list_point) else "Chưa có thông tin đánh giá về tài xế",
            "detail": None
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class ListRateShipper(GenericAPIView):
    queryset = Rate.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RateSerializer

    def get(self, request, shipper_id):
        data = Rate.objects.filter(order__shipper_id=shipper_id)
        rates = list(data)
        list_point = []
        for rate in rates:
            list_point.append(rate.rate)

        response = {
            "status": "success",
            "data": {"mean": mean(list_point),
                     "len": len(list_point),
                     "rates": RateSerializer(data, many=True).data
                     }
            if len(list_point)
            else "Chưa có thông tin đánh giá về tài xế",
            "detail": None
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class ShipperInfoViewSet(APIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, shipper_id):
        shipper = Shipper.objects.filter(pk=shipper_id)
        if shipper.exists():
            response = {
                "status": "success",
                "data": ShipperInfoSerializer(shipper.first()).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status": "error",
            "data": None,
            "detail": "shipper_id không hợp lệ!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
