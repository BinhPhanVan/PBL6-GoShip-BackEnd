
from rest_framework import serializers
from .models import Payment, Category, Status, Order, Rate
from UserApi.serializers import AddressSerializer
from UserApi.serializers import ShipperSerializer, CustomerSerializer
from UserApi.models import Customer
from AccountApi.models import Account
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['phone_number']
        
class CustomerOrderSerializer(serializers.ModelSerializer):
    account = PhoneNumberSerializer(required = True)
    class Meta:
        model = Customer
        fields = '__all__'


class RateSerializer(serializers.Serializer):
    feedback = serializers.CharField(default = 'Good job')
    rate = serializers.IntegerField(default = 5)
    order_id = serializers.IntegerField(default = 10)


class OrderDetailSerializer(serializers.ModelSerializer):
    address_start = AddressSerializer(required=True)
    address_end = AddressSerializer(required=True)
    payment = PaymentSerializer(required=True)
    customer = CustomerOrderSerializer(required=True)
    category = CategorySerializer(required=True)
    status = StatusSerializer(required=True)
    rate =  RateSerializer(required=True)
    class Meta:
        model= Order
        fields = '__all__' 
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'customer': {
                'read_only': True
            },
            'created_at': {
                'read_only': True
            },
            'updated_at': {
                'read_only': True
            },
            'status': {
                'read_only': True
            },
            'shipper': {
                'read_only': True
            },
            'cost': {
                'read_only': True
            },
            'rate': {
                'read_only': True
            },
        }


class OrderSerializer(serializers.ModelSerializer):
    address_start = AddressSerializer(required=True)
    address_end = AddressSerializer(required=True)
    class Meta:
        model= Order
        fields = '__all__' 
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'customer': {
                'read_only': True
            },
            'created_at': {
                'read_only': True
            },
            'updated_at': {
                'read_only': True
            },
            'shipper': {
                'read_only': True
            },
            'cost': {
                'read_only': True
            },
            'is_rating': {
                'read_only': True
            },
            'status': {
                'read_only': True
            },
            'rate': {
                'read_only': True
            },
        }


class  OrderIdSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class PaySerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_desc = serializers.CharField()

