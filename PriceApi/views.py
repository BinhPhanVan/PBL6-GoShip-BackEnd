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
from drf_yasg import openapi
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
@swagger_auto_schema(method = 'GET',manual_parameters=[
        openapi.Parameter('start',in_= openapi.IN_QUERY,description='Address Start',type=openapi.TYPE_STRING,example = 'latitude, longitude'),
        openapi.Parameter('end',in_= openapi.IN_QUERY,description='Address End',type=openapi.TYPE_STRING, example = 'latitude, longitude')])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def get_distance(request):
    try:

        start_address = request.query_params.get('start').split(',')
        end_address = request.query_params.get('end').split(',')
        latitude1 = float(start_address[0])
        latitude2 = float(end_address[0])
        longitude1 = float(start_address[1])
        longitude2 = float(end_address[1])
        distance = getDistanceBetweenPointsNew(latitude1, longitude1, latitude2, longitude2, 'kilometers')
    except Exception:
        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)
    response = {
        "status": "success",
        "data": distance,
        "detail": None
    }
    return Response(response, status=status.HTTP_200_OK)

@swagger_auto_schema(method = 'GET',manual_parameters=[
        openapi.Parameter('distance',in_= openapi.IN_QUERY,description='Distance (m)',type=openapi.TYPE_STRING,example = '11'),
        openapi.Parameter('is_protected',in_= openapi.IN_QUERY,description='is_protected (1 or 2)',type=openapi.TYPE_INTEGER, example = 1)])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def get_price(request, *args, **kwargs):
    try: 
        price =  Price.objects.first()
        km = float(request.query_params.get('distance'))
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
        if int(request.query_params.get('is_protected')) == 2:
           extra_price =  money * (price.price_protect / 100)
    except Exception:
        response = {
            "status": "error",
            "data": None,
            "detail": "Dữ liệu không hợp lệ!"
        }
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response)
    response = {
        "status": "success",
        "data": {
            'detail': 'Dữ liệu hợp lệ',
            'distance': max_km,
            'money': money,
            'extra_price': extra_price,
            'total': money + extra_price
        },
        "detail": None
    }
    return Response(response, status=status.HTTP_200_OK)
    
