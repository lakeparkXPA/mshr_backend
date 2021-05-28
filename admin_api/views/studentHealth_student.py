import os
import datetime

from django.db.models import Q
from django.http import FileResponse, JsonResponse

from rest_framework.decorators import *

from rest_framework.status import *

from admin_api.permissions import *
from admin_api.serializers import *

from admin_api.custom import *
from django.db import connection
import pandas as pd
import numpy as np
import json
from django.db import transaction


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_list(request):

    """학생 리스트 조회"""
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
def school_list(request):

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
def student_add(request):
    """학생 등록 api"""

    student_data = request.POST.get('info','')
    student_data = json.loads(student_data)

    file_data = request.FILES.get('file','')

    if file_data:
        student_data['pic'] =file_data

    """학생뿐만 아니라 졸업생역시 min이 중복되는지여부 체크해야함."""
    if Student.objects\
            .filter(medical_insurance_number=student_data['medical_insurance_number'])\
            .exists() or \
            Graduate.objects.\
                    filter(medical_insurance_number=student_data['medical_insurance_number'])\
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
def student_get(request,student_id):

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
def student_get_img(request,student_id):

    "학생 수정시 학생 이미지 로딩 api"

    if student_id is None:
        raise exceptions.ValidationError("Student_id error.")

    student_pic = Student.objects.get(student_id=student_id).pic
    if student_pic is None:
        return Response()

    return FileResponse(student_pic)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def min_check(request):

    """min 중복여부 체크 api"""
    min = request.POST.get('min','')

    if not min:
        raise exceptions.ValidationError("min error")


    data = {}
    """학생뿐만 아니라 졸업생역시 min이 중복되는지여부 체크해야함."""
    if Student.objects\
            .filter(medical_insurance_number=min)\
            .exists() or \
            Graduate.objects.\
                    filter(medical_insurance_number=min)\
                    .exists():
        data['check'] = False
    else:
        data['check'] = True


    return Response(data)


@api_view(['PUT'])
@permission_classes([AllAuthenticated])
def student_modify(request):
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
def student_delete(request,student_id):

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
#@permission_classes([AllAuthenticated])
def student_addAll(request):

    """csv 파일 파싱 후 저장 """

    file = request.FILES.get('file','')
    if not file:
        raise exceptions.ValidationError('file error')
    print(file)
    file_check = str(file)


    file_check = file_check.split('.')

    if file_check[-1] =='xlsx':
        df = pd.read_excel(file,engine='openpyxl')
    else:
        df = pd.read_excel(file)



    df = df.drop(['No'],axis=1)
    print(df)
    school_id_list = list(set(df['School ID']))
    print(school_id_list)
    df = df.rename({})
    for school_id in school_id_list:
        school_fk = School.objects.filter(school_id=school_id).values('id').first()
        #print(connection.queries)

        df['School ID'] = df['School ID'].apply(lambda x:school_fk['id'] if x==school_id else x)


    df.columns = ['school_fk','student_name',
                  'grade','grade_class','student_number','date_of_birth',
                  'gender','medical_insurance_number','village','contact','parents_name']
    df = df.replace(np.NAN,'')
    print(df)

    bulk_list = []
    bulk_fk_list = []
    #print(df.to_dict())

    for i in df.index:
        data = {}
        #student = Student()
        for j, k in enumerate(df.columns):
            #print(k)
            #student.k = df.values[i][j]
            if k =='date_of_birth':
                data[k] = df.values[i][j].date()
            else:
                data[k] = df.values[i][j]

        student_obj = AddStudentSerializer(data=data,partial=True)

        if student_obj.is_valid():
            student_obj.save()
        else:
            print(student_obj.errors)


        #     print(student_obj.validated_data)
        #     student = Student()
        #     for key,value in student_obj.validated_data.items():
        #         student.key = value
        #
        #     bulk_list.append(student)

        #print(bulk_list)

    # print(bulk_list)
    # with transaction.atomic():
    #     Student.objects.bulk_create(bulk_list)



    return Response()

