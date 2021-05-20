
from django.shortcuts import render
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

from mshr_backend.settings import ALGORITHM, SECRET_KEY



@api_view(['POST','GET'])
@permission_classes([IsMaster])
def test(request):

    return Response()





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




@api_view(['POST'])
@permission_classes([AllAuthenticated])
def dashboard_filter(request):
    '''
    대시보드 province, district,school 필터링
    '''
    filter = request.POST.get('filter','')
    province = request.POST.get('province','')
    district = request.POST.get('district', '')
    school = request.POST.get('school_name', '')

    data = {}

    try:
        user_level = User.objects.get(user_id = request.POST.get('user_id')).user_level
        print(user_level)

    except exceptions as e:
        return JsonResponse(str(e), status=HTTP_400_BAD_REQUEST)





    if filter == 'province' and (user_level is 0):

        """Province 검색 할 경우"""

        try:
            province_list = Province.objects.all().values('province')
            data['province'] = []

            for order_list in province_list:

                data['province'].append(order_list['province'])
                print(data)

        except:
            raise exceptions.ValidationError


    elif filter =='district' and (user_level in[0,1]):
        """Province 검색 할 경우"""

        if not province:
            raise exceptions.ValidationError


        province_obj =Province.objects.\
                        prefetch_related('district_set').\
                        get(province=province)

        district_list = DistrictSerializer(province_obj.district_set.all(),many=True).data


        data['district'] = []

        for order_list in district_list:
            data['district'].append(order_list['district'])

        if 1 in [1,2]:
            print(True)


    elif filter == 'school' and (user_level in [0,1,2,3]):
        print()
        if not province or not district:
            raise exceptions.ValidationError


        school_obj = School.objects.select_related('area_fk').\
            select_related('area_fk__province_fk').\
            select_related('area_fk__district_fk').\
            filter(area_fk__province_fk__province=province,
                   area_fk__district_fk__district=district).values('school_id','school_name')

        data['schools'] = []

        for obj in school_obj:
            print(obj)
            school_info = {}

            school_info['school_name'] = obj['school_name']
            school_info['school_id'] =obj['school_id']

            data['schools'].append(school_info)




    return JsonResponse(data, status=HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice_list(request):
    """
    공지사항 list 조회 api
    """

    try:
        notice_obj = Notice.objects.all()
        notice_serializer = NoticeListSerializer(notice_obj,many=True)

        notice_list = {}
        notice_list['notice'] = notice_serializer.data


    except:
        raise exceptions.ValidationError

    return Response(notice_list)



