from rest_framework import serializers
from .models import *


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }
    
class PositionSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class GetPriceSerializer(serializers.Serializer):
    distance = serializers.FloatField()
    is_protected = serializers.IntegerField()

class GetDistanceSerializer(serializers.Serializer):
    start_address = PositionSerializer()
    end_address = PositionSerializer()
