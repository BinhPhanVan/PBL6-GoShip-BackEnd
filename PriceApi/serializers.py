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
    
        