from rest_framework import generics, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer, ShipperSerializer, ConfirmShipperSerializer, LoginSerializer, CustomerSerializer
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
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        if not Account.objects.filter(phone_number=request.data.get('phone_number')).exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            account = serializer.save()
            token = MyTokenObtainPairSerializer.get_token(account)
            response = {
                'role': account.role,
                'phone_number': account.phone_number,
                'access_token': str(token),
                "details": "Đăng ký thành công!"
            }
            return Response(response,  status=status.HTTP_202_ACCEPTED)

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
            account = authenticate(
                request,
                username=serializer.validated_data['phone_number'],
                password=serializer.validated_data['password']
            )
            if account:
                refresh = MyTokenObtainPairSerializer.get_token(account)
                data = {
                    'account': RegisterSerializer(account).data,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response({"details": "Đăng xuất thành công!"}, status=status.HTTP_204_NO_CONTENT)


class ConfirmShipper(GenericAPIView):
    queryset = Shipper.objects.all()
    permission_classes = [permissions.IsAuthenticated, ShipperPermission]
    serializer_class = ConfirmShipperSerializer

    def post(self, request):
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


class ShipperViewSet(viewsets.ViewSet,GenericAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer

    def get_permissions(self):
        if self.action == 'detail':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='shipper-detail')
    def detail(self, request):
        shipper = Shipper.objects.filter(
            account__phone_number=request.user.phone_number)
        if shipper.exists():
            return Response(ShipperSerializer(shipper.first()).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            'detail': 'Dữ liệu không hợp lệ!'
        })


class CustomerViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated,
                          CustomerPermission, AdminPermission]
