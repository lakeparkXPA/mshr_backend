import jwt

from rest_framework import permissions, authentication

from rest_framework import exceptions

from mshr_backend.settings import ALGORITHM, SECRET_KEY
from admin_api.models import *







class AllAuthenticated(permissions.BasePermission):

    """모든 권한 존재하는 계정 """

    def has_permission(self, request, view):

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0,1,2,3,4) and tokenverify(auth[1]):
                    return True

        return False




class IsMaster(permissions.BasePermission):

    """Master 계정 권한 부여"""

    def has_permission(self, request, view):
        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0) and tokenverify(auth[1]):
                    return True

        return False

class OverProvince(permissions.BasePermission):

    """Province 계정 권한 부여"""

    def has_permission(self, request, view):

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0,1) and tokenverify(auth[1]):
                    return True

        return False


class OverDistrict(permissions.BasePermission):

    """District 계정 권한 부여"""

    def has_permission(self, request, view):

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0,1,2) and tokenverify(auth[1]):
                    return True

        return False


class OverCommune(permissions.BasePermission):

    """Commune 계정 권한 부여"""

    def has_permission(self, request, view):

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0,1,2,3) and tokenverify(auth[1]):
                    return True

        return False


class OverSchool(permissions.BasePermission):

    """School 계정 권한 부여"""

    def has_permission(self, request, view):

        if request.META.get('HTTP_AUTHORIZATION') is None:
            return False
        else:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            user_id = request.META.get('HTTP_USER_ID','')
            if user_id is None:
                return False

            if len(auth) ==1:
                raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')

            elif len(auth) ==2:
                if permission_check(user_id,0,1,2,3,4) and tokenverify(auth[1]):
                    return True

        return False




def permission_check(user_id,*level):

    try:
        user_level = User.objects.get(user_id=user_id).user_level

        if user_level in level:
            return True
        else:
            return False

    except:
        raise exceptions.ValidationError


def tokenverify(token):

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        if decoded_token['auth'] == 'access':
            return True
        else:
            return False
    except:
        raise exceptions.AuthenticationFailed('Token Expired')








