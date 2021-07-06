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
    Login Api (http user id header 필요)
    '''
    #pw = request.POST.get('password','')
    request_json = json.loads(request.body)

    pw = request_json.get('password','')

    data = {}
    data['province'] = ""
    data['district'] = ""
    data['commune'] = ""
    data['school_name'] = ""
    data['school_id'] = ""


    header = {}
    if not pw:

        #data['status']=3
        header['HTTP_X_CSTATUS']= 3
        return Response(headers=header, status=HTTP_400_BAD_REQUEST)
        #raise exceptions.ValidationError(data)


    try:
        obj = User.objects.get(user_id=request_json['user_id'])
    except:
        #data['status']=2
        print("user id error")
        header['HTTP_X_CSTATUS']=2
        return Response(headers=header, status=HTTP_400_BAD_REQUEST)


    user = LoginSerializer(obj).data

    if user['user_level'] == 1:
        area = Area.objects.select_related('province_fk').get(area_id = user['area_fk'])
        data['province'] = area.province_fk.province

    elif user['user_level'] == 2:
        area = Area.objects.select_related('province_fk')\
                    .select_related('district_fk').get(area_id = user['area_fk'])
        data['province'] = area.province_fk.province
        data['district'] = area.district_fk.district

    elif user['user_level'] == 3:
        area = Area.objects.select_related('province_fk')\
                    .select_related('district_fk')\
                    .select_related('commune_clinic_fk').get(area_id = user['area_fk'])
        data['province'] = area.province_fk.province
        data['district'] = area.district_fk.district
        data['commune'] = area.commune_clinic_fk.commune_clinic

    elif user['user_level'] == 4:
        area = Area.objects.select_related('province_fk')\
                    .select_related('district_fk')\
                    .select_related('commune_clinic_fk').get(area_id = user['area_fk'])
        data['province'] = area.province_fk.province
        data['district'] = area.district_fk.district
        data['commune'] = area.commune_clinic_fk.commune_clinic
        school = School.objects.filter(id = user['school_fk']).values('school_name','school_id').first()
        data['school_name'] = school['school_name']
        data['school_id'] = school['school_id']
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
            data['user_level'] = user['user_level']
            obj.token = refresh_token.decode()
            obj.save()

            log(request,typ='Log in', content='Login success')
            header['HTTP_X_CSTATUS'] = 0
            return Response(data, headers=header,status=HTTP_200_OK)


        else:
            #data['status'] = 1
            print("password incorrupt")
            header['HTTP_X_CSTATUS'] =1
            return Response(data,headers=header,status=HTTP_200_OK)

    except Exception as e:
        #data['status'] = 4
        print(str(e))
        header['HTTP_X_CSTATUS']=4
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes((AllAuthenticated,))
def account_detail(request):
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            raise ValueError(1)

        user = User.objects.filter(user_id__exact=user_id)

        user_replace = user.extra(select={'user_mobile': "coalesce(user_mobile, '')",
                                          'email_address': "coalesce(user.email_address, '')"})

        user_select = user_replace.values('user_id', 'user_name', 'user_tel', 'user_mobile', 'email_address')

        res = Response(user_select, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['POST'])
@permission_classes((AllAuthenticated,))
def account_edit(request):

    request_json = json.loads(request.body)

    user_id = request_json.get('user_id','')
    user_name = request_json.get('user_name','')
    user_tel = request_json.get('user_tel', '')
    user_mobile = request_json.get('user_mobile', '')
    email_address = request_json.get('email_address', '')


    user_pk = User.objects.get(user_id__exact=user_id).id

    account = User.objects.get(id=user_pk)
    account.user_name = user_name
    account.user_tel = user_tel
    if user_mobile:
        account.user_mobile = user_mobile
    if email_address:
        account.email_address = email_address

    account.save()
    # TODO---- Enable block later
    log(request, typ='Add school', content='Update user ' + user_id)

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res



@api_view(['POST'])
@permission_classes((AllAuthenticated,))
def account_pw(request):
    try:
        request = json.loads(request.body)
        user_id = request.get('user_id','')
        pw_old = request.get('pw_old','')
        pw_new = request.get('pw_new','')

        pw_db = User.objects.get(user_id__exact=user_id).password

        pw_check = bcrypt.checkpw(pw_old.encode('utf-8'), pw_db.encode('utf-8'))

        if not pw_check:
            raise ValueError(2)

        user_pw = User.objects.get(user_id__exact=user_id)
        user_pw.password = bcrypt.hashpw(pw_new.encode('utf-8'), bcrypt.gensalt(5)).decode('utf-8')
        user_pw.save()

        res = Response(status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


