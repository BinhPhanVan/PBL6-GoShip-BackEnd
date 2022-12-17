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
from django.core.paginator import Paginator
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import get_price
from BaseApi.FirebaseManager import sendNotificationUser


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

    def list(self, request, *args, **kwargs):
        payment = Payment.objects.all()
        serializer = PaymentSerializer(payment, many=True)
        response = {
            "status": "success",
            "data": serializer.data,
            "detail": None
        }
        return Response(response, status=status.HTTP_200_OK)


class CategoryView(viewsets.ModelViewSet,):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdminPermission()]

    def list(self, request, *args, **kwargs):
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        response = {
            "status": "success",
            "data": serializer.data,
            "detail": None
        }
        return Response(response, status=status.HTTP_200_OK)


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

    def list(self, request, *args, **kwargs):
        stt = Status.objects.all()
        serializer = StatusSerializer(stt, many=True)
        response = {
            "status": "success",
            "data": serializer.data,
            "detail": None
        }
        return Response(response, status=status.HTTP_200_OK)


class OrderView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]
    serializer_class = OrderSerializer
    pagination_class = BasePagination

    def get(self, request):
        phone_number = request.user.phone_number
        order = Order.objects.filter(
            customer__account__phone_number=phone_number).order_by('-created_at')
        paginator = Paginator(order, 10)
        page = request.GET.get('page')
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(1)
        serializer = OrderSerializer(orders, many=True)
        response = {
            "status": "success",
            "data": {
                "orders": serializer.data,
                "total": paginator.count,
                "num_pages": paginator.num_pages,
            },
            "detail": None,
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
                cost=get_price(serializer.validated_data.get('distance'), Category.objects.filter(
                    id=request.data.get('category')).first().is_protected),
                description=serializer.validated_data.get('description'),
                status=Status.objects.filter(id=1).first()
            )
            order.save()
            firebase_database.sendNotificationToShipper(lat=float(
                order.address_start.latitude), long=float(order.address_start.longitude), order_id=order.id)
            response = {
                "status": "success",
                "data":  OrderSerializer(order).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!",
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class OrderDetailView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderIdSerializer

    def get(self, request, order_id):
        order = Order.objects.filter(id=order_id)
        if order.exists():
            order = order.first()
            response = {
                "status": "success",
                "data":  OrderDetailSerializer(order).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": "error",
            "data": None,
            "detail": "Đơn hàng không tồn tại!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class OrderStatusView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page',in_= openapi.IN_QUERY,description='Page Number',type=openapi.TYPE_INTEGER),
        openapi.Parameter('status_id',in_= openapi.IN_QUERY,description='Status ID',type=openapi.TYPE_INTEGER)])
    def get(self, request):
        status_id = int(request.query_params.get('status_id'))
        page = int(request.query_params.get('page'))
        if  status_id > 5:
            response = {
                "status": "error",
                "data": None,
                "detail": "status_id không tồn tại"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role == 1:
            orders = Order.objects.filter(status_id=status_id, customer__account__phone_number = request.user.phone_number).order_by('-created_at')
        if request.user.role == 2:
            orders = Order.objects.filter(status_id=status_id, shipper__account__phone_number  = request.user.phone_number).order_by('-created_at')
        paginator = Paginator(orders, 10)
        response = {
            "status": "success",
            "detail": None,
            }
        try:
            orders = paginator.page(page)
            serializer = OrderDetailSerializer(orders, many=True)
            response = {
            "status": "success",
            "data":{
                "orders": serializer.data,
                "total": paginator.count,
                },
            "detail": None
            }
        except:
            response["data"] = {
                "orders": [],
                "total": paginator.count,
            },
        return Response(response, status=status.HTTP_200_OK)

class OrderReceiveView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = OrderIdSerializer

    def patch(self, request):
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
                    "detail": None
                }
                customer_phone_number = order.customer.account.phone_number
                account = Account.objects.get(
                    phone_number=customer_phone_number)
                sendNotificationUser(
                    account.token_device, customer_phone_number, order.id, 2)
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "status": "error",
                    "data": None,
                    "detail": "Đơn hàng đã có người nhận!"
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {
            "status": "error",
            "data": None,
            "detail": "Đơn hàng không tồn tại!"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class OrderDelivery(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    serializer_class = OrderIdSerializer

    def patch(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=request.data.get('order_id'))
            if order.shipper.account.phone_number == request.user.phone_number:
                if order.status.id == 2:
                    order.status = Status.objects.get(pk=3)
                    order.save()
                    response = {
                        "status": "success",
                        "data":  OrderSerializer(order).data,
                        "detail": None
                    }
                    customer_phone_number = order.customer.account.phone_number
                    account = Account.objects.get(
                        phone_number=customer_phone_number)
                    sendNotificationUser(
                        account.token_device, customer_phone_number, order.id, 3)
                    return Response(response, status=status.HTTP_202_ACCEPTED)
                else:
                    response = {
                        "status": "error",
                        "data": None,
                        "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!"
                    }
            else:
                response = {
                    "status": "error",
                    "data": None,
                    "detail": "Đây không phải là đơn hàng của bạn!"
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Đơn hàng không hợp lệ!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class OrderRequestConfirmDone(APIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShipperPermission]
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id',in_= openapi.IN_QUERY,description='ORDER ID',type=openapi.TYPE_INTEGER)])
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=request.query_params.get('order_id'))
            if order.shipper.account.phone_number == request.user.phone_number:
                if order.status.id == 3:
                    response = {
                        "status": "success",
                        "data":  OrderSerializer(order).data,
                        "detail": None
                    }
                    customer_phone_number = order.customer.account.phone_number
                    account = Account.objects.get(
                        phone_number=customer_phone_number)
                    sendNotificationUser(
                        account.token_device, customer_phone_number, order.id, 5)
                    return Response(response, status=status.HTTP_202_ACCEPTED)
                else:
                    response = {
                        "status": "error",
                        "data": None,
                        "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!"
                    }
            else:
                response = {
                    "status": "error",
                    "data": None,
                    "detail": "Đây không phải là đơn hàng của bạn!"
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Đơn hàng không hợp lệ!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class OrderConfirmDone(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]
    serializer_class = OrderIdSerializer

    def patch(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=request.data.get('order_id'))
            if order.customer.account.phone_number == request.user.phone_number:
                if order.status.id == 3:
                    order.status = Status.objects.get(pk=5)
                    order.save()
                    response = {
                        "status": "success",
                        "data":  OrderSerializer(order).data,
                        "detail": None
                    }
                    shipper_phone_number = order.shipper.account.phone_number
                    account = Account.objects.get(
                        phone_number=shipper_phone_number)
                    sendNotificationUser(
                        account.token_device, shipper_phone_number, order.id, 6)
                    return Response(response, status=status.HTTP_202_ACCEPTED)
                else:
                    response = {
                        "status": "error",
                        "data": None,
                        "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!"
                    }
            else:
                response = {
                    "status": "error",
                    "data": None,
                    "detail": "Đây không phải là đơn hàng của bạn!"
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Đơn hàng không hợp lệ!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RatingOrder(GenericAPIView):
    queryset = Rate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]
    serializer_class = RateSerializer

    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=request.data.get('order'))
            if order.customer.account.phone_number == request.user.phone_number:
                if order.status.id == 5:
                    if order.is_rating:
                        response = {
                        "status": "error",
                        "data":  None,
                        "detail": "Đơn hàng đã được đánh giá!"
                        }
                        return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
                    rate = Rate.objects.create(order=order,
                                                feedback=request.data.get(
                                                    'feedback'),
                                                rate=int(request.data.get('rate')))
                    order.is_rating = True
                    order.save()
                    response = {
                        "status": "success",
                        "data":  RateSerializer(rate).data,
                        "detail": None
                    }
                    return Response(response, status=status.HTTP_202_ACCEPTED)
                else:
                    response = {
                        "status": "error",
                        "data": None,
                        "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!"
                    }
            else:
                response = {
                    "status": "error",
                    "data": None,
                    "detail": "Đây không phải là đơn hàng của bạn!"
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Đơn hàng không hợp lệ!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

