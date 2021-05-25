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
    commune = request.POST.get('commune','')
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


        except:
            raise exceptions.ValidationError


    elif filter =='district' and (user_level in[0,1]):
        """district 검색 할 경우"""

        if not province:
            raise exceptions.ValidationError


        province_obj =Province.objects.\
                        prefetch_related('district_set').\
                        get(province=province)

        district_list = DistrictSerializer(province_obj.district_set.all(),many=True).data


        data['district'] = []

        for order_list in district_list:
            data['district'].append(order_list['district'])



    elif filter =='commune' and (user_level in [0,1,2]):
        "commune 검색할경우 "

        if not province or not district:
            raise exceptions.ValidationError

        commune_obj = CommuneClinic.objects.select_related('district_fk').\
                        filter(district_fk__district=district)

        commune_list = CommuneSerializer(commune_obj,many=True).data
        print(connection.queries)
        data['commune'] = []
        for commune in commune_list:
            data['commune'].append(commune['commune_clinic'])





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
        notice_list_obj = Notice.objects.all()
        notice_serializer = NoticeListSerializer(notice_list_obj,many=True)

        notice_list = {}
        notice_list['notice'] = notice_serializer.data


    except:
        raise exceptions.ValidationError

    return Response(notice_list)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice(request,notice_id):


    """
    공지사항 상세조회 api
    """

    try:

        notice_obj = Notice.objects.prefetch_related('noticefile_set').\
                                    get(notice_id=notice_id)

        notice = NoticeSerializer(notice_obj).data
        files = NoticeFileSerializer(notice_obj.noticefile_set.all(),many=True).data

        file_list = []

        for file in files:
            file_list.append(file['file_name'])

        notice['file_name'] = file_list

    except:
        raise exceptions.ValidationError


    return Response(notice)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice_img(request,notice_id,file_name):
    """
    공지사항 이미지 다운로드 API
    """
    try:
        img = open(STATIC_DIR+f'/notice/{notice_id}/{file_name}','rb')

    except:
        raise exceptions.NotFound


    return FileResponse(img,as_attachment=True)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_student_list(request):

    user_id = request.POST.get('user_id','')
    school_id = request.POST.get('school_id','')
    grade = request.POST.get('grade','')
    name_id = request.POST.get('name_id','')


    q = Q()
    data = {}
    """필터링 조건으로 조회할 경우"""
    if school_id or grade or name_id:

        if school_id:
            q.add(Q(school_fk__id=school_id),q.AND)
        if grade:
            q.add(Q(grade=grade),q.AND)

        if name_id:
            q.add(Q(student_name=name_id) | Q(medical_insurance_number=name_id),q.AND)

        try:
            students_obj = Student.objects.select_related('school_fk').\
                            filter(q)

        except:
            raise exceptions.ValidationError

        student_serializer = StudentSerializer(students_obj,many=True)

        student_list = student_serializer.data
        data['students'] = student_list


    else:

        """유저가 확인 가능한 전체 조회할 경우"""

        if user_id:
            user = User.objects.select_related('area_fk').\
                                    filter(user_id=user_id).\
                                    values('user_level','area_fk','school_fk',
                                    'area_fk__province_fk','area_fk__district_fk',
                                    'area_fk__commune_clinic_fk')[0]


            try:
                if user['user_level']==0:

                    """유저가 마스터 계정일경우"""
                    students_obj = Student.objects.all()
                    student_list = []
                    student_serializer = StudentSerializer(students_obj,many=True).data
                    student_list.append(student_serializer)

                    data['students']=student_list




                elif user['user_level']==1:

                    """유저가 province계정 인 경우"""



                    area_list = Area.objects.prefetch_related('school_set').\
                                    prefetch_related('school_set__student_set').\
                                    filter(province_fk=user['area_fk__province_fk'])


                    student_list = []

                    for area in area_list:
                        for school in area.school_set.all():
                            student_serializer = StudentSerializer(school.student_set.all(),many=True).data
                            student_list.append(student_serializer)

                    data['students'] = student_list



                elif user['user_level']==2:

                    area_list = Area.objects.prefetch_related('school_set').\
                                    prfetch_related('school_set__student_set').\
                                    filter(province_fk=user['area_fk__province_fk'],
                                            district_fk=user['area_fk__district_fk'])

                    student_list = []

                    for area in area_list:
                        for school in area.school_set.all():
                            student_serializer = StudentSerializer(school.student_set.all(),many=True).data
                            student_list.append(student_serializer)

                    data['students'] = student_list



                elif user['user_level']==3:

                    """유저가 commune_clinic 계정 인 경우"""

                    area_list = Area.objects.prefetch_related('school_set').\
                                    prfetch_related('school_set__student_set').\
                                    filter(province_fk=user['area_fk__province_fk'],
                                            district_fk=user['area_fk__district_fk'],
                                            commune_clinic_fk=user['area_fk__commune_clinic_fk'])

                    student_list = []

                    for area in area_list:
                        for school in area.school_set.all():
                            student_serializer = StudentSerializer(school.student_set.all(),many=True).data
                            student_list.append(student_serializer)

                    data['students'] = student_list



                elif user['user_level']==4:

                    student = Student.objects.select_related('school_fk').\
                                    filter(school_fk=user['school_fk'])


                    student_list = []
                    student_serializer = StudentSerializer(student.all(),many=True).data

                    student_list.append(student_serializer)
                    data['students'] = student_list




            except:
                raise exceptions.ValidationError



        else:
            raise exceptions.ValidationError



    return Response(data)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_school_list(request):

    """Student 학교 명단 조회 시 사용 API"""
    user_id = request.POST.get('user_id','')

    try:

        user = User.objects.select_related('area_fk'). \
                filter(user_id__exact=user_id). \
                values('user_level', 'area_fk', 'school_fk',
                   'area_fk__province_fk', 'area_fk__district_fk',
                   'area_fk__commune_clinic_fk')[0]
    except:
        raise exceptions.ValidationError


    data = {}
    try:


        if user['user_level'] == 0:

            schools_obj = School.objects.all()


        elif user['user_level'] == 1:

            """province"""


            schools_obj =School.objects.select_related('area_fk').\
                        filter(area_fk__province_fk=user['area_fk__province_fk'])

        elif user['user_level']==2:

            """district"""

            schools_obj = School.objects.select_related('area_fk').\
                        filter(area_fk__province_fk=user['area_fk__province_fk'],
                                area_fk__district_fk=user['area_fk__district_fk'])


        elif user['user_level']==3:

            """commune"""

            schools_obj = School.objects.select_related('area_fk').\
                        filter(area_fk__province_fk=user['area_fk__province_fk'],
                                area_fk__district_fk=user['area_fk__district_fk'],
                                area_fk__commune_clinic_fk=user['area_fk__commune_clinic_fk'])

        elif user['user_level']==4:

            """"school"""
            schools_obj = School.objects.filter(id=user['school_fk'])

    except:
        raise exceptions.ValidationError



    school_serializer = SchoolListSerializer(schools_obj,many=True).data



    data['schools'] = school_serializer

    return Response(data)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_student_add(request):
    """학생 등록 api"""

    student_data = request.POST.get('info','')
    student_data = json.loads(student_data)

    file_data = request.FILES.get('file','')

    if file_data:
        student_data['pic'] =file_data

    if Student.objects\
            .filter(medical_insurance_number=student_data['medical_insurance_number'])\
            .exists():

        return Response("already exist.",status=HTTP_409_CONFLICT)


    student_obj = AddStudentSerializer(data=student_data,partial=True)
    if student_obj.is_valid():
         student_obj.save()
    else:
        raise exceptions.ValidationError

    return Response(status=HTTP_201_CREATED)





@api_view(['GET'])
@permission_classes([AllAuthenticated])
def studentHealth_student_get(request,student_id):

    """학생 수정시 학생 정보 로딩 api"""

    print(student_id)
    print(student_id)
    if student_id is None:
        raise exceptions.ValidationError("Student_id error.")


    student_obj = Student.objects.get(student_id=student_id)
    student_serializer = AddStudentSerializer(student_obj).data
    print(student_serializer)

    student_serializer.pop('pic')



    return Response(student_serializer)

@api_view(['GET'])
@permission_classes([AllAuthenticated])
def studentHealth_student_get_img(request,student_id):

    "학생 수정시 학생 이미지 로딩 api"

    if student_id is None:
        raise exceptions.ValidationError("Student_id error.")

    student_pic = Student.objects.get(student_id=student_id).pic
    if student_pic is None:
        return Response()

    return FileResponse(student_pic)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_min_check(request):

    """min 중복여부 체크 api"""
    min = request.POST.get('min','')
    print(min)
    if not min:
        raise exceptions.ValidationError("min error")


    data = {}

    try:
        obj = Student.objects.get(medical_insurance_number=min)
        data['check'] = False

    except Student.DoesNotExist:
        data['check']= True


    return Response(data)


@api_view(['PUT'])
@permission_classes([AllAuthenticated])
def studentHealth_student_modify(request):
    """학생 정보 수정시 사용 api"""

    student_data = request.POST.get('info','')
    student_data = json.loads(student_data)

    file_data = request.FILES.get('file','')

    if file_data:
        student_data['pic'] = file_data

    student_id = student_data.pop('student_id')
    try:
        student_obj = Student.objects.get(student_id=student_id)

    except:
        raise exceptions.ValidationError("Does not exist.")



    origin_img = student_obj.pic


    student_serializer = AddStudentSerializer(student_obj,data=student_data,partial=True)

    try:
        if student_serializer.is_valid():
            student_serializer.save()

            """이미지를 새로 갱신한다면 원래 이미지는 삭제 """
            if file_data and os.path.isfile(origin_img.path):
                os.remove(origin_img.path)
    except:
        raise exceptions.ValidationError("data insert error")


    return Response(status=HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([AllAuthenticated])
def studentHealth_student_delete(request,student_id):

    if student_id is None:
        raise exceptions.ValidationError("Student_id error")


    try:
        student_obj = Student.objects.\
                        prefetch_related('checkup_set').\
                        get(student_id=student_id)
    except:
        raise exceptions.ValidationError("Student does not exist.")


    checkup_set = student_obj.checkup_set.all()




    graduate_obj = model_to_dict(student_obj)
    graduate_obj.pop('student_id')
    min = graduate_obj['medical_insurance_number']

    print(graduate_obj)
    if graduate_obj['pic'] == None or graduate_obj['pic'] =='':
        graduate_obj.pop('pic')

    try:

        with transaction.atomic():

            graduate_serializer = GraduateSerializer(data = graduate_obj,partial=True)

            if graduate_serializer.is_valid():
                graduate_serializer.save()

                graduate_obj = Graduate.objects.\
                                get(medical_insurance_number=min)
                for checkup in checkup_set:
                    checkup.graduate_fk = graduate_obj
                    checkup.save()

                student_obj.delete()
            else:

                raise exceptions.ValidationError

    except Exception as e:
        raise exceptions.ValidationError(str(e))


    return Response(status=HTTP_200_OK)








@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_student_addAll(request):

    """csv 파일 파싱 후 저장 """

    file = request.FILES.get('file','')
    if not file:
        raise exceptions.ValidationError('file error')
    print(file)
    print("test")


    """ openpyxl은 xlsx만 파싱가능, xlrd? 는 xls만 파싱가능..
    뭘써야할지 고민입니다"""
    df = pd.read_excel(file)

    df = df.drop(['No'],axis=1)
    df = df.drop([''])
    # df.columns = ['school_fk','student_id','student_name',
    #               'grade','grade_class','student_number','date_of_birth',
    #               'gender','medical_insurance_number','village','contact','parents_name']
    students = []

    for i in df.index:
        data = {}
        for j, k in enumerate(df.columns):
            data[k] = df.values[i][j]
        students.append(data)

    print(students)







    return Response()


