from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.response import Response
from OrderApi import views
from rest_framework.decorators import action
from .models import *
from .serializers import *
import math
from rest_framework.generics import GenericAPIView
from rest_framework import  permissions, status
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from drf_yasg.utils import swagger_auto_schema
from numpy import sin, cos, arccos, pi, round

def rad2deg(radians):
    degrees = radians * 180 / pi
    return degrees

def deg2rad(degrees):
    radians = degrees * pi / 180
    return radians

def getDistanceBetweenPointsNew(latitude1, longitude1, latitude2, longitude2, unit = 'miles'):
    
    theta = longitude1 - longitude2
    
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) + 
            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        )
    )
    
    if unit == 'miles':
        return round(distance, 2)
    if unit == 'kilometers':
        return round(distance * 1.609344, 2)



# Create your views here.
@swagger_auto_schema(methods=['post'], request_body=GetDistanceSerializer)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def get_distance(request):
    try:
        start_address = request.data.get('start_address')
        end_address = request.data.get('end_address')
        latitude1 = float(start_address["latitude"])
        latitude2 = float(end_address["latitude"])
        longitude1 = float(start_address["longitude"])
        longitude2 = float(end_address["longitude"])
        abc = getDistanceBetweenPointsNew(latitude1, longitude1, latitude2, longitude2, 'kilometers')
    except Exception:
        return Response(data={
            'detail': 'Dữ liệu không hợp lệ!',
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={
            'detail': 'Dữ liệu hợp lệ',
            'distance': abc
        }, status=status.HTTP_202_ACCEPTED)

@swagger_auto_schema(methods=['post'], request_body=GetPriceSerializer)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def get_price(request, *args, **kwargs):
    try: 
        price =  Price.objects.first()
        km = float(request.data.get('distance'))
        initial_price = price.initial_price
        anchor = price.anchor
        extra_price = 0
        money = 0
        max_km  = int(round(km))
        for i in range(1, max_km + 1):
            if i <= anchor:
                money += initial_price
            if i > anchor and (i - anchor) * price.price_percent <= 70:
                money += price.extra_price * (100 - (i - anchor) * price.price_percent) / 100; 
            if i > anchor and (i - anchor) * price.price_percent > 70:
                money += price.extra_price * 30 / 100;   
        print(money)
        if request.data.get('is_protected') == 1:
           extra_price =  money * (price.price_protect / 100)
    except Exception:
        return Response(data={
            'detail': 'Dữ liệu không hợp lệ!',
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={
            'detail': 'Dữ liệu hợp lệ',
            'distance': max_km,
            'money': money,
            'extra_price': extra_price,
            'total': money + extra_price
        }, status=status.HTTP_202_ACCEPTED)
    
    