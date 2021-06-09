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
from admin_api.package.log import log
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.parsers import MultiPartParser
import bcrypt
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
    #try:
        # user_id = request.META.get('HTTP_USER_ID','')
        # if not user_id:
        #     raise exceptions.ValidationError
        # obj = User.objects.get(user_id= user_id)

    data = {}
    header = {}
    obj = User.objects.get(user_id=request.data['user_id'])

    """데이터 베이스 내 갱신 토큰 확인 """
    verified_token = RefreshTokenSerializer(obj).data['token']


    try:
        decoded_token = jwt.decode(verified_token, SECRET_KEY, ALGORITHM)
    except:
        #data['status'] =1
        header['HTTP_X_CSTATUS'] = 1
        print("token expired")
        return Response(headers= header,status=HTTP_401_UNAUTHORIZED)
       #raise exceptions.NotAuthenticated(data)


    if request.META.get('HTTP_AUTHORIZATION') is None:
        #data['status']=2
        header['HTTP_X_CSTATUS'] = 2
        return Response(headers=header, status=HTTP_401_UNAUTHORIZED)
        #raise exceptions.NotAuthenticated(data)

    print("test")
    client_token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]

    try:
        client_decoded_token = jwt.decode(client_token,SECRET_KEY,ALGORITHM)
    except:
        #data['status'] =1
        print("token expired")
        header['HTTP_X_CSTATUS'] =1
        return Response(headers=header, status=HTTP_401_UNAUTHORIZED)
        #raise exceptions.NotAuthenticated(data)

    if decoded_token['auth'] == 'refresh' and \
        client_decoded_token['auth'] =='refresh' and \
        decoded_token == client_decoded_token:

        payload = {}

        payload['auth'] = 'access'

        payload['exp'] = datetime.datetime.utcnow() + \
                        datetime.timedelta(hours=1)

        access_token = jwt.encode(payload, SECRET_KEY, ALGORITHM)


        data['access_token'] = access_token
        #data['status'] = 0
        header['HTTP_X_CSTATUS'] = 0

        return Response(data,headers=header,status=HTTP_200_OK)

    else:
        data['status']=1
        header['HTTP_X_CSTATUS'] = 1
        return Response(data,headers=header, status=HTTP_401_UNAUTHORIZED)





@api_view(['POST'])
@permission_classes([AllowAny]) #모든 사람에게 권한 허용
def login(request):

    '''
    Login Api
    '''
    #pw = request.POST.get('password','')
    request = json.loads(request.body)

    pw = request.get('password','')

    data = {}
    header = {}
    if not pw:

        #data['status']=3
        header['HTTP_X_CSTATUS']= 3
        return Response(headers=header, status=HTTP_400_BAD_REQUEST)
        #raise exceptions.ValidationError(data)


    try:
        obj = User.objects.get(user_id=request.data['user_id'])
    except:
        #data['status']=2
        print("user id error")
        header['HTTP_X_CSTATUS']=2
        return Response(headers=header, status=HTTP_400_BAD_REQUEST)


    user = LoginSerializer(obj).data
    try:
        if bcrypt.checkpw(pw.encode("utf-8"),user['password'].encode("utf-8")):
        #if hashlib.sha256(request.data['password'].encode()).hexdigest() == user['password']:
        #if True:
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




            data['access_token'] = access_token
            data['refresh_token'] = refresh_token

            obj.token = refresh_token.decode()
            obj.save()

            # log(request,typ='Log in', content='Login success')
            header['HTTP_X_CSTATUS'] = 0
            return Response(data, headers=header,status=HTTP_200_OK)


        else:
            #data['status'] = 1
            print("password incorrupt")
            header['HTTP_X_CSTATUS'] =1
            return Response(data,headers=header,status=HTTP_200_OK)

    except Exception as e:
        data['status'] = 4
        print(str(e))
        header['HTTP_X_CSTATUS']=4
        return Response(data,headers=header,status=HTTP_400_BAD_REQUEST)






