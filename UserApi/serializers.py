from rest_framework import serializers
from .models import Account, Customer, Shipper, Address
import time
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, account):
        token = super().get_token(account)
        token['role'] = account.role
        token['phone_number'] = account.phone_number
        return token


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("phone_number", "password", "role")
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        account = Account.objects.create(**validated_data)
        account.password = make_password(validated_data['password'])
        account.save()
        text_time = round(time.time()*1000)
        if validated_data['role'] == 1:
            name_default = 'Customer' + str(text_time)[:10]
            customer = Customer.objects.create(account= account, name=name_default)
            customer.save()
        elif validated_data['role'] == 2:
            name_default = 'Shipper' + str(text_time)[:10]
            shipper = Shipper.objects.create(
                account=account, name=name_default)
            shipper.save()
        return account

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ShipperSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    class Meta:
        model = Shipper
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    class Meta:
        model = Customer
        fields = ['name', 'address', 'gender', 'avatar_url', 'distance_view']

class ConfirmShipperSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    class Meta:
        model = Shipper
        fields = ['name', 'address', 'gender', 'url_identification_top',
                  'url_identification_back', 'identification_info', 'url_face_video']

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UpdateDeviceToken(serializers.Serializer):
    token_device = serializers.CharField(required=True)

class ChangePassWordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    repeat_password = serializers.CharField(max_length=128)

