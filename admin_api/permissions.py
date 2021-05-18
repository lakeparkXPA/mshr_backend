import jwt
from django.http import JsonResponse
from django.utils.encoding import smart_text
from rest_framework import permissions, authentication
from rest_framework.status import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, BaseJSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework import exceptions
from rest_framework.response import *
from django.http import HttpResponse
from admin_api import custom
from mshr_backend.settings import ALGORITHM, SECRET_KEY
from admin_api.models import *




class DefaultAuthentication(authentication.BaseAuthentication):
    #www_authenticate_realm = 'api'

    '''' 기본 인증 클래스 '''


    def authenticate(self,request):

        """None의경우 권한요청을 시도한것이 아님 . 로그인시"""

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return None

        else:
            token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
            if self.tokenverify(token):
                #print("pass")
                return (None, None)
            #토큰값이 다른경우
            else:
                raise exceptions.AuthenticationFailed('No Authenticated')

    def tokenverify(self,token):

        try:

            decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
            if decoded_token['auth'] == 'access' or \
                    decoded_token['auth'] == 'refresh':
                return True
            else:
                return False
        except:
            raise exceptions.AuthenticationFailed('Token Expired')









"""모든 권한 존재하는 계정 """

class AllAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
            exceptions.AuthenticationFailed('No Authenticated')

        else:
            token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
            if self.tokenverify(token):
                return True
            else:
                return False

    def tokenverify(self, token):

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
            if decoded_token['auth'] == 'access':
                return True
            else:
                return False
        except:
            raise exceptions.AuthenticationFailed('Token Expired')




class IsMaster(permissions.BasePermission):

    """Master 계정 권한 부여"""

    def has_permission(self, request, view):

        user_id = request.META.get('HTTP_USER_ID','')

        if user_id:
            if permission_check(user_id,0):
                return True

        return False

class IsProvince(permissions.BasePermission):

    """Province 계정 권한 부여"""

    def has_permission(self, request, view):

        user_id = request.META.get('HTTP_USER_ID', '')

        if user_id:
            if permission_check(user_id, 1):
                return True

        return False


class IsDistrict(permissions.BasePermission):

    """District 계정 권한 부여"""

    def has_permission(self, request, view):

        user_id = request.META.get('HTTP_USER_ID', '')

        if user_id:
            if permission_check(user_id, 2):
                return True

        return False


class IsCommune(permissions.BasePermission):

    """Commune 계정 권한 부여"""

    def has_permission(self, request, view):

        user_id = request.META.get('HTTP_USER_ID', '')

        if user_id:
            if permission_check(user_id, 3):
                return True

        return False


class IsSchool(permissions.BasePermission):

    """School 계정 권한 부여"""

    def has_permission(self, request, view):

        user_id = request.META.get('HTTP_USER_ID', '')

        if user_id:
            if permission_check(user_id, 4):
                return True

        return False




def permission_check(user_id,level):

    try:

        user_level = User.objects.get(user_id=user_id).user_level

        if user_level==level:
            return True
        else:
            return False

    except:
        raise exceptions.ValidationError











