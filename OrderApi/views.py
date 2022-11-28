from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from BaseApi.permissions import *
from .models import *
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
import BaseApi.FirebaseManager as firebase_database


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
            return Response({
                'detail': 'Thành công',
                'order': OrderSerializer(order).data}, status=status.HTTP_200_OK)
        return Response(data={
            'detail': 'Dữ liệu không hợp lệ!',
        }, status=status.HTTP_400_BAD_REQUEST)
