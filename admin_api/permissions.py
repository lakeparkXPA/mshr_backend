import jwt
from django.http import JsonResponse
from django.utils.encoding import smart_text
from rest_framework import permissions
from rest_framework.status import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, BaseJSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework import exceptions
from rest_framework.response import *
from django.http import HttpResponse
from admin_api import custom
from mshr_backend.settings import ALGORITHM, SECRET_KEY

class IsMaster(permissions.BasePermission):

    """Master 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
             return False

        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

        if tokenVerify(token,'master'):
            return True

        return False


class IsProvince(permissions.BasePermission):

    """Province 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
             return False

        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

        if tokenVerify(token,'province'):
            return True

        return False

class IsDistrict(permissions.BasePermission):

    """District 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
             return False

        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

        if tokenVerify(token,'district'):
            return True

        return False

class IsCommune(permissions.BasePermission):

    """Commune 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
             return False

        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

        if tokenVerify(token,'commune'):
            return True

        return False

class IsSchool(permissions.BasePermission):

    """School 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
             return False

        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

        if tokenVerify(token,'school'):
            return True

        return False


def tokenVerify(token,grade):

    """토큰 내부 값 검증 및 기간 확인"""

    try:
        decoded_token = jwt.decode(token,SECRET_KEY,ALGORITHM)

        if decoded_token['user_level']== grade:
            return True
        else:
            return False
    except:
        raise exceptions.NotAuthenticated


