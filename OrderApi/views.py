import requests
from datetime import datetime
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status, permissions

from OrderApi.vnpay import vnpay
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
from .utils import *
from BaseApi.FirebaseManager import sendNotificationUser
from django.db.models import Q


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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderShipperSerializer
    pagination_class = BasePagination

    def get(self, request):
        phone_number = request.user.phone_number
        if request.user.role == 1:
            order = Order.objects.filter(
                customer__account__phone_number=phone_number).order_by('-created_at')
        else:
            order = Order.objects.filter(
                shipper__account__phone_number=phone_number).order_by('-created_at')
        paginator = Paginator(order, 10)
        page = request.GET.get('page')
        try:
            orders = paginator.page(page)
        except:
            orders = paginator.page(1)
        serializer = OrderDetailSerializer(orders, many=True)
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
        try:
            order = Order(
                customer=Customer.objects.filter(
                    account__phone_number=request.user.phone_number).first(),
                address_start=Address.objects.create(
                    **request.data.get('address_start')),
                address_end=Address.objects.create(
                    **request.data.get('address_end')),
                distance=request.data.get('distance'),
                customer_notes=request.data.get(
                    'customer_notes'),
                img_order=request.data.get('img_order', None),
                payment=Payment.objects.filter(
                    id=request.data.get('payment')).first(),
                category=Category.objects.filter(
                    id=request.data.get('category')).first(),
                cost=get_price(request.data.get('distance'), Category.objects.filter(
                    id=request.data.get('category')).first().is_protected),
                description=request.data.get('description', None),
                status=Status.objects.filter(id=1).first()
            )
            order.save()
            shipper_find = check_shipper(request.data.get('shipper'))
            if shipper_find:
                print(shipper_find.account.token_device)
                firebase_database.sendNotificationUser(
                    shipper_find.account.token_device, request.data.get('shipper'),  order_id=order.id, type=1)
            else:
                firebase_database.sendNotificationToShipper(lat=float(
                    order.address_start.latitude), long=float(order.address_start.longitude), order_id=order.id)
            response = {
                "status": "success",
                "data":  OrderSerializer(order).data,
                "detail": None
            }
            return Response(response, status=status.HTTP_200_OK)
        except ValueError as err:
            response = {
                "status": "error",
                "data": None,
                "detail": "Vị trí kinh độ và vĩ độ phải dưới dạng số thực!",
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)
        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Dữ liệu không hợp lệ!",
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', in_=openapi.IN_QUERY, description='Order ID', type=openapi.TYPE_INTEGER)])
    def delete(self, request):
        try:
            order = Order.objects.filter(
                (Q(shipper__account__phone_number=request.user.phone_number) |
                 Q(customer__account__phone_number=request.user.phone_number)) &
                Q(id=int(request.query_params.get('order_id'))))
            account = Account.objects.get(
                phone_number=request.user.phone_number)
            if order.exists():
                order = order.first()
                if order.status == Status.objects.get(id=1) or order.status == Status.objects.get(id=2):
                    status_old = order.status
                    order.status = Status.objects.get(id=4)
                    order.save()
                    response = {
                        "status": "success",
                        "data": "Đơn hàng đã được huỷ thành công!",
                        "detail": None,
                    }
                    if status_old == Status.objects.get(id=2):
                        if account.role == 1:
                            account_shipper = Account.objects.get(
                                phone_number=order.shipper.account.phone_number)
                            sendNotificationUser(
                                account_shipper.token_device, account_shipper.phone_number, order.id, 8)
                        else:
                            account_customer = Account.objects.get(
                                phone_number=order.customer.account.phone_number)
                            sendNotificationUser(
                                account_customer.token_device, account_customer.phone_number, order.id, 4)

                    return Response(status=status.HTTP_200_OK, data=response)
                else:
                    response = {
                        "status": "error",
                        "data": None,
                        "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!",
                    }
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=response)
            else:
                raise Exception
        except:
            response = {
                "status": "error",
                "data": None,
                "detail": "Đây không phải là đơn hàng của bạn!",
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
        openapi.Parameter('page', in_=openapi.IN_QUERY,
                          description='Page Number', type=openapi.TYPE_INTEGER),
        openapi.Parameter('status_id', in_=openapi.IN_QUERY, description='Status ID', type=openapi.TYPE_INTEGER)])
    def get(self, request):
        try:
            page = int(request.query_params.get('page'))
        except:
            page = 1
        try:
            status_id = int(request.query_params.get('status_id'))
        except:
            status_id = -1
        if status_id > 5:
            response = {
                "status": "error",
                "data": None,
                "detail": "status_id không tồn tại"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if status_id != -1:
            if request.user.role == 1:
                orders = Order.objects.filter(
                    status_id=status_id, customer__account__phone_number=request.user.phone_number).order_by('-created_at')
            if request.user.role == 2:
                orders = Order.objects.filter(
                    status_id=status_id, shipper__account__phone_number=request.user.phone_number).order_by('-created_at')
        else:
            orders = Order.objects.filter(
                Q(shipper__account__phone_number=request.user.phone_number) | Q(customer__account__phone_number=request.user.phone_number)).order_by('-created_at')
        paginator = Paginator(orders, 5)
        response = {
            "status": "success",
            "detail": None,
        }
        try:
            orders = paginator.page(page)
            serializer = OrderDetailSerializer(orders, many=True)
            response = {
                "status": "success",
                "data": {
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
                    "detail": "Trạng thái đơn hàng không hỗ trợ hành động này!"
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
        openapi.Parameter('order_id', in_=openapi.IN_QUERY, description='ORDER ID', type=openapi.TYPE_INTEGER)])
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
                    order.save()
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
    serializer_class = RateCustomSerializer

    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=int(request.data.get('order_id')))
            if order.customer.account.phone_number == request.user.phone_number:
                if order.status.id == 5:
                    if order.is_rating:
                        response = {
                            "status": "error",
                            "data":  None,
                            "detail": "Đơn hàng đã được đánh giá!"
                        }
                        return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
                    rate = Rate.objects.create(
                        feedback=request.data.get(
                            'feedback'),
                        rate=int(request.data.get('rate')))
                    rate.save()
                    order.is_rating = True
                    order.rate = rate
                    order.save()
                    response = {
                        "status": "success",
                        "data":  OrderDetailSerializer(order).data,
                        "detail": None
                    }
                    shipper_phone_number = order.shipper.account.phone_number
                    account = Account.objects.get(
                        phone_number=shipper_phone_number)
                    sendNotificationUser(
                        account.token_device, shipper_phone_number, order.id, 7)
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
                "detail": "Đơn hàng không tồn tại!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RateDetailView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if order.customer.account.phone_number == request.user.phone_number or order.shipper.account.phone_number == request.user.phone_number:
                response = {
                    "status": "success",
                    "data":  RateSerializer(order.rate).data,
                    "detail": None
                }
                return Response(response, status=status.HTTP_200_OK)
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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PayOrder(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]
    serializer_class = PaySerializer

    def post(self, request):
        try:
            order_id = request.data.get('order_id')
            order = Order.objects.get(id=order_id)
            if order.customer.account.phone_number == request.user.phone_number:
                amount = order.cost
                order_desc = request.data.get('order_desc')
                order_type = 'other'
                bank_code = "NCB"
                ipaddr = get_client_ip(request)
                vnp = vnpay()
                vnp.requestData['vnp_Version'] = '2.1.0'
                vnp.requestData['vnp_Command'] = 'pay'
                vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
                vnp.requestData['vnp_Amount'] = amount * 100
                vnp.requestData['vnp_CurrCode'] = 'VND'
                vnp.requestData['vnp_TxnRef'] = order_id
                vnp.requestData['vnp_OrderInfo'] = order_desc
                vnp.requestData['vnp_OrderType'] = order_type
                # Check language, default: vn
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
                if bank_code and bank_code != "":
                    vnp.requestData['vnp_BankCode'] = bank_code
                vnp.requestData['vnp_CreateDate'] = datetime.now().strftime(
                    '%Y%m%d%H%M%S')  # 20150410063022
                vnp.requestData['vnp_IpAddr'] = ipaddr
                vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
                vnpay_payment_url = vnp.get_payment_url(
                    settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
                # print(vnpay_payment_url)
                return Response({
                    "status": "success",
                    "data": vnpay_payment_url,
                    "detail": "Đang thực hiện thanh toán"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "data": '',
                    "detail": "Thanh toán thất bại!"
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                "status": "error",
                "data": "",
                "detail": "Đơn hàng không hợp lệ!"
            }, status=status.HTTP_400_BAD_REQUEST)
