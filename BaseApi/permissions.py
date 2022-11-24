from rest_framework.permissions import BasePermission
import jwt
from django.conf import settings
from GoShip import settings

class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            print(request.user.role)
            if request.user.role == 3:
                return True
            return False
        except Exception:
            print(str(Exception))
            return False

class IsShipperPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role == 2:
                return True
            return False
        except Exception:
            print(str(Exception))
            return False
class IsCustomerPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.role == 1:
                return True
            return False
        except Exception:
            print(str(Exception))
            return False
