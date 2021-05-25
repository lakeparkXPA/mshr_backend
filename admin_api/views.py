import os

from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from pandas.tests.io.excel.test_openpyxl import openpyxl
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.status import *
from rest_framework.views import *
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
# Create your views here.
from admin_api.models import *
from admin_api.permissions import *
from admin_api.serializers import *
import hashlib, jwt
from django.contrib.auth import authenticate
import datetime
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.parsers import MultiPartParser

from mshr_backend.settings import ALGORITHM, SECRET_KEY, BASE_DIR
from mshr_backend.settings import STATIC_DIR
from admin_api.custom import *
from django.db import connection
import pandas as pd
import json
from django.db import transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):

    '''
    토큰 재발급 API
    '''
    try:
        # user_id = request.META.get('HTTP_USER_ID','')
        # if not user_id:
        #     raise exceptions.ValidationError
        # obj = User.objects.get(user_id= user_id)


        obj = User.objects.get(user_id=request.data['user_id'])
        verified_token = RefreshTokenSerializer(obj).data['token']

        decoded_token = jwt.decode(verified_token, SECRET_KEY, ALGORITHM)

        try:
            if request.META.get('HTTP_AUTHORIZATION') is None:
                raise exceptions.NotAuthenticated()

            else:
                client_token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]


                client_decoded_token = jwt.decode(client_token,SECRET_KEY,ALGORITHM)

                if decoded_token['auth'] == 'refresh' and \
                    client_decoded_token['auth'] =='refresh' and \
                        decoded_token == client_decoded_token:

                    payload = {}
                    payload['auth'] = 'access'

                    payload['exp'] = datetime.datetime.utcnow() + \
                                    datetime.timedelta(hours=1)

                    access_token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

                    data = {}
                    data['access_token'] = access_token

                    return Response(data)

                else:
                    return Response('Error: invalidated token', status=HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response('Error: ' + str(e),status=HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response('Error : ' + str(e), status=HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([AllowAny]) #모든 사람에게 권한 허용
def login(request):

    '''
    Login Api
    '''

    try:

        obj = User.objects.get(user_id=request.data['user_id'])
        user = LoginSerializer(obj).data

        if hashlib.sha256(request.data['password'].encode()).hexdigest() == user['password']:

            payload = {}
            payload['auth'] = 'access'


            payload['exp'] = datetime.datetime.utcnow() + \
                             datetime.timedelta(hours=24)

            access_token = jwt.encode(payload,SECRET_KEY,ALGORITHM)


            refresh_payload ={}
            refresh_payload['auth'] = 'refresh'

            refresh_payload['exp'] = datetime.datetime.utcnow() + \
                                     datetime.timedelta(hours=24)

            refresh_token = jwt.encode(refresh_payload,SECRET_KEY,ALGORITHM)


            data = {}

            data['access_token'] = access_token
            data['refresh_token'] = refresh_token

            obj.token = refresh_token.decode()
            obj.save()

            return Response(data)


        else:
            return Response("password incorrupt",status=HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response('Error : ' + str(e),status=HTTP_400_BAD_REQUEST)






