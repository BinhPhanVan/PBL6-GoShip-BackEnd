from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from BaseApi.permissions import *
from .models import *
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
import BaseApi.FirebaseManager as firebase_database
from .paginator import BasePagination
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema


class PaymentView(viewsets.ViewSet,
                  generics.ListCreateAPIView,
                  generics.CreateAPIView,
                  generics.RetrieveAPIView,
                  generics.UpdateAPIView,
                  generics.DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdminPermission()]


class CategoryView(viewsets.ModelViewSet,):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdminPermission()]


class StatusView(viewsets.ViewSet,
                 generics.ListCreateAPIView,
                 generics.CreateAPIView,
                 generics.RetrieveAPIView,
                 generics.UpdateAPIView,
                 generics.DestroyAPIView):
    queryset = Status.objects.all()
    permission_classes = [IsAdminPermission]
    serializer_class = StatusSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdminPermission()]


class OrderView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]
    serializer_class = OrderSerializer
    pagination_class = BasePagination

    def get(self, request):
        phone_number = request.user.phone_number
        order = Order.objects.filter(
            customer__account__phone_number=phone_number)
        serializer = OrderSerializer(order, many=True)
        response = {
            "status": "success",
            "data": serializer.data,
            "message": None
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = Order(
                customer=Customer.objects.filter(
                    account__phone_number=request.user.phone_number).first(),
                address_start=Address.objects.create(
                    **request.data.get('address_start')),
                address_end=Address.objects.create(
                    **request.data.get('address_end')),
                distance=serializer.validated_data.get('distance'),
                customer_notes=serializer.validated_data.get('customer_notes'),
                img_order=serializer.validated_data.get('img_order'),
                payment=Payment.objects.filter(
                    id=request.data.get('payment')).first(),
                category=Category.objects.filter(
                    id=request.data.get('category')).first(),
                cost=20000,
                description=serializer.validated_data.get('description'),
                status=Status.objects.filter(id=1).first()
            )
            order.save()
            firebase_database.sendNotificationToShipper(lat=float(
                order.address_start.latitude), long=float(order.address_start.longitude), order_id=order.id)
            response = {
                "status": "success",
                "data":  OrderSerializer(order).data,
                "message": None
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "message": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class OrderDetailView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = OrderIdSerializer

    def get(self, request, order_id):
        order = Order.objects.filter(id=order_id)
        if order.exists():
            order = order.first()
            order.status = Status.objects.get(id=2)
            order.shipper = Shipper.objects.get(
                account__phone_number=request.user.phone_number)
            order.save()
            response = {
                "status": "success",
                "data":  OrderSerializer(order).data,
                "message": None
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "message": "Đơn hàng không tồn tại!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class OrderReceiveView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = OrderIdSerializer

    def post(self, request):
        order = Order.objects.filter(id=request.data.get('order_id'))
        if order.exists():
            order = order.first()
            if order.status.id == 1:
                order.status = Status.objects.get(id=2)
                order.shipper = Shipper.objects.get(
                    account__phone_number=request.user.phone_number)
                order.save()
                response = {
                    "status": "success",
                    "data":  OrderSerializer(order).data,
                    "message": None
                }
            else:
                response = {
                    "status": "success",
                    "data": None,
                    "message": "Đơn hàng đã có người nhận!"
                }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "message": "Đơn hàng không tồn tại!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
