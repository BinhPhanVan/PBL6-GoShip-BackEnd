from rest_framework import serializers
from .models import Payment, Category, Status, Order
from UserApi.serializers import AddressSerializer
from UserApi.serializers import ShipperSerializer, CustomerSerializer
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
class OrderSerializer(serializers.ModelSerializer):
    address_start = AddressSerializer(required=True)
    address_end = AddressSerializer(required=True)
    shipper = ShipperSerializer(required=True)
    customer = CustomerSerializer(required=True)
    payment = PaymentSerializer(required=True)
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
        }



