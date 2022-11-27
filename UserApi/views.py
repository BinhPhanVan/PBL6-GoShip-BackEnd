from rest_framework import generics, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from BaseApi.permissions import *
from .models import Account, Address, Shipper, Customer
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from rest_framework.generics import GenericAPIView

# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Account.objects.all()
    permission_classes = (IsCustomerPermission, IsShipperPermission)
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
            token = MyTokenObtainPairSerializer.get_token(account)
            response = {
                'role': account.role,
                'phone_number': account.phone_number,
                'access_token': str(token),
                'refresh_token': str(MyTokenObtainPairSerializer.get_token(account)),
                "detail": "Đăng ký thành công!"
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)

        return Response(
            {
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
                return Response(data, status=status.HTTP_200_OK)
            return Response({
                'detail': 'Tài khoản hoặc mật khẩu không hợp lệ!',
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'error_messages': serializer.errors,
            'error_code': 400,
            'detail': 'Dữ liệu không hợp lệ!'
        }, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        logout(request)
        return Response({"detail": "Đăng xuất thành công!"}, status=status.HTTP_204_NO_CONTENT)


class ConfirmShipper(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = ConfirmShipperSerializer

    def put(self, request):

        account = Account.objects.filter(
            phone_number=request.user.phone_number)
        if account.exists():
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
                           identification_info=request.data.get(
                               'identification_info'),
                           url_face_video=request.data.get('url_face_video'),
                           confirmed=1
                           )

            return Response(ShipperSerializer(shipper.first()).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            'detail': 'Dữ liệu không hợp lệ!'
        })


class ShipperViewSet(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = ShipperSerializer

    def get(self, request):
        shipper = Shipper.objects.filter(
            account__phone_number=request.user.phone_number)
        if shipper.exists():
            return Response(ShipperSerializer(shipper.first()).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            'detail': 'Dữ liệu không hợp lệ!'
        })


class CustomerViewSet(GenericAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsCustomerPermission]
    serializer_class = CustomerSerializer

    def get(self, request):
        customer = Customer.objects.filter(
            account__phone_number=request.user.phone_number)
        if customer.exists():
            return Response(CustomerSerializer(customer.first()).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            'detail': 'Dữ liệu không hợp lệ!'
        })

    def patch(self, request):
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
            )
            return Response(CustomerSerializer(customer.first()).data, status=status.HTTP_200_OK)
        return Response(data={
            "detail": "Truy vấn không hợp lệ!"
        }, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeviceTokenView(GenericAPIView):
    serializer_class = UpdateDeviceToken
    queryset = Account.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        token_device = request.data.get('token_device')
        account = Account.objects.filter(
            phone_number=request.user.phone_number)
        print(request.user.phone_number)

        if account.exists():
            account.update(token_device=token_device)
            return Response(status=status.HTTP_200_OK)
        return Response(
            data={"detail": "Dữ liệu không hợp lệ!"},
            status=status.HTTp_400_BAD_REQUEST)
