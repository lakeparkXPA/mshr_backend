import os
import datetime

from django.db.models import Q, F
from django.http import FileResponse, JsonResponse, HttpResponse
import xlwt

from rest_framework.decorators import *

from rest_framework.status import *

from admin_api.permissions import *
from admin_api.serializers import *
from admin_api.package.log import *
from admin_api.custom import *
from django.db import connection
import pandas as pd
import numpy as np
import json
from django.db import transaction


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_list(request):
    user_id = request.META.get('HTTP_USER_ID', '')
    """학생 리스트 조회"""
    request = json.loads(request.body)

    user_id = request.get('user_id','')
    province = request.get('province', '')
    district = request.get('district', '')
    commune = request.get('commune', '')
    school_id = request.get('school_id','')
    grade = request.get('grade','')
    name_id = request.get('name','')

    header = {}

    q = Q()

    if school_id or grade or name_id or province or district or commune:
        if province:
            q.add(Q(school_fk__area_fk__province_fk__province=province), q.AND)
        if district:
            q.add(Q(school_fk__area_fk__district_fk__district=district), q.AND)
        if commune:
            q.add(Q(school_fk__area_fk__commune_clinic_fk__commune_clinic=commune), q.AND)
        if school_id:
            q.add(Q(school_fk__id=school_id),q.AND)
        else:
            user_level = User.objects.get(user_id__iexact=user_id).user_level

            if user_level == 0:
                pass
            elif user_level == 1:
                area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
                area_id = Area.objects.filter(Q(province_fk__exact=area)).values('area_id')
                school_id = School.objects.filter(area_fk__in=area_id).values('id')
                q.add(Q(school_fk__id__in=school_id), q.AND)
            else:
                area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.district_fk
                area_id = Area.objects.filter(Q(district_fk__exact=area)).values('area_id')
                school_id = School.objects.filter(area_fk__in=area_id).values('id')
                q.add(Q(school_fk__id__in=school_id), q.AND)

        if grade:
            q.add(Q(grade=grade),q.AND)

        if name_id:
            q.add(Q(student_name=name_id) | Q(medical_insurance_number=name_id),q.AND)

        try:
            students_obj = Student.objects.select_related('school_fk').\
                            filter(q)

        except:
            #data['status'] = 3
            header['HTTP_X_CSTATUS'] = 3
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)

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
                    students_obj = Student.objects.select_related('school_fk')

                elif user['user_level'] == 1:
                    """유저가 province계정 인 경우"""
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk').\
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'])

                elif user['user_level']==2:
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk'). \
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'],
                               school_fk__area_fk__district_fk=user['area_fk__district_fk'])

                elif user['user_level']==3:
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk'). \
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'],
                               school_fk__area_fk__district_fk=user['area_fk__district_fk'],
                               school_fk__area_fk__commune_clinic_fk=user['area_fk__commune_clinic_fk'])
                    """유저가 commune_clinic 계정 인 경우"""

                elif user['user_level']==4:

                    students_obj = Student.objects.select_related('school_fk').\
                                    filter(school_fk=user['school_fk'])

            except:
                header['HTTP_X_CSTATUS'] = 2
                return Response(headers=header, status=HTTP_400_BAD_REQUEST)




        else:
            header['HTTP_X_CSTATUS'] = 1
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)

    header['HTTP_X_CSTATUS'] = 0

    student_list = students_obj.values('student_id', 'medical_insurance_number', 'student_name', 'date_of_birth', 'gender', 'grade', 'grade_class', school_id=F('school_fk__school_id'), school_name=F('school_fk__school_name'))

    return Response(student_list,headers=header,status=HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_listDownload(request):

    """학생 리스트 다운로드 """

    request_json = json.loads(request.body)

    user_id = request_json.get('user_id','')
    school_id = request_json.get('school_id','')
    grade = request_json.get('grade','')
    name_id = request_json.get('name','')
    province = request_json.get('province')
    district = request_json.get('district')
    commune = request_json.get('commune')




    q = Q()
    data = {}
    header = {}


    if province:
        qa = Q()
        province_id = Province.objects.get(province=province).province_id
        qa.add(Q(province_fk=province_id), qa.AND)
        if district:
            district_id = District.objects.get(district=district).district_id
            qa.add(Q(district_fk=district_id), qa.AND)
            if commune:
                commune_id = CommuneClinic.objects.get(commune_clinic=commune).commune_clinic_id
                qa.add(Q(commune_clinic_fk=commune_id), qa.AND)
        area = Area.objects.filter(qa).values('area_id')
        q.add(Q(area_fk__in=area), q.AND)

    """필터링 조건으로 조회할 경우"""
    if school_id or grade or name_id:

        if school_id:
            q.add(Q(school_fk__id=school_id),q.AND)
        else:
            user_level = User.objects.get(user_id__iexact=user_id).user_level

            if user_level == 0:
                pass
            elif user_level == 1:
                area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
                area_id = Area.objects.filter(Q(province_fk__exact=area)).values('area_id')
                school_id = School.objects.filter(area_fk__in=area_id).values('id')
                q.add(Q(school_fk__id__in=school_id), q.AND)
            else:
                area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.district_fk
                area_id = Area.objects.filter(Q(district_fk__exact=area)).values('area_id')
                school_id = School.objects.filter(area_fk__in=area_id).values('id')
                q.add(Q(school_fk__id__in=school_id), q.AND)
        if grade:
            q.add(Q(grade=grade),q.AND)

        if name_id:
            q.add(Q(student_name=name_id) | Q(medical_insurance_number=name_id),q.AND)

        try:
            students_obj = Student.objects.select_related('school_fk').\
                            filter(q)

        except:
            header['HTTP_X_CSTATUS'] = 3
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    else:

        """유저가 확인 가능한 전체 조회할 경우"""

        if user_id:
            user = User.objects.select_related('area_fk').\
                                    filter(user_id=user_id).\
                                    values('user_level','area_fk','school_fk',
                                    'area_fk__province_fk','area_fk__district_fk',
                                    'area_fk__commune_clinic_fk')[0]


            try:
                if user['user_level'] == 0:

                    """유저가 마스터 계정일경우"""
                    students_obj = Student.objects.select_related('school_fk')

                elif user['user_level'] == 1:
                    """유저가 province계정 인 경우"""
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk'). \
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'])

                elif user['user_level'] == 2:
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk'). \
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'],
                               school_fk__area_fk__district_fk=user['area_fk__district_fk'])

                elif user['user_level'] == 3:
                    students_obj = Student.objects.select_related('school_fk').select_related('area_fk'). \
                        filter(school_fk__area_fk__province_fk=user['area_fk__province_fk'],
                               school_fk__area_fk__district_fk=user['area_fk__district_fk'],
                               school_fk__area_fk__commune_clinic_fk=user['area_fk__commune_clinic_fk'])
                    """유저가 commune_clinic 계정 인 경우"""

                elif user['user_level'] == 4:

                    students_obj = Student.objects.select_related('school_fk'). \
                        filter(school_fk=user['school_fk'])



            except:
                header['HTTP_X_CSTATUS'] = 2
                return Response(headers=header, status=HTTP_400_BAD_REQUEST)



        else:
            header['HTTP_X_CSTATUS'] = 1
            return Response(headers=header, status=HTTP_400_BAD_REQUEST)


    response = HttpResponse(content_type="application/vnd.ms-excel")

    today = datetime.datetime.today().strftime("%Y-%m-%d")

    filename = 'StudentList_{}.xls'.format(today)

    response['Content-Disposition'] = "attachment; filename={}".format(filename)

    wb = xlwt.Workbook(encoding='utf-8')

    ws = wb.add_sheet("Students")

    row_num = 0


    font_style = xlwt.XFStyle()

    #headef font are bold
    font_style.font.bold = True

    columns = ['Student ID','Name','School ID','School Name','Grade','Class','Student Number','DOB',
                  'Gender','MIN','Village','Contact','Parents']

    for idx, col_name in enumerate(columns):
        ws.write(row_num,idx,col_name,font_style)

    student_list = students_obj.annotate(school_id=F('school_fk__school_id'), school_name=F('school_fk__school_name')).\
        values_list('student_id', 'student_name', 'school_id', 'school_name','grade', 'grade_class', 'student_number',
               'date_of_birth', 'gender', 'medical_insurance_number', 'village', 'contact','parents_name')

    if len(student_list) == 1:
        data_students = [student_list]
    else:
        data_students = student_list
    for row in data_students:
        row_num+=1
        for col,value in enumerate(row):
            ws.write(row_num,col,value)



    wb.save(response)

    log(request,typ='Download Student List',
        content='Download Student List file' )

    return response



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def school_list(request):

    """Student 학교 명단 조회 시 사용 API"""
    request = json.loads(request.body)

    user_id = request.get('user_id','')



    data = {}
    header = {}

    try:

        user = User.objects.select_related('area_fk'). \
                filter(user_id__exact=user_id). \
                values('user_level', 'area_fk', 'school_fk',
                   'area_fk__province_fk', 'area_fk__district_fk',
                   'area_fk__commune_clinic_fk')[0]
    except:
        #data['status'] = 1

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



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
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    school_serializer = SchoolListSerializer(schools_obj,many=True).data



    data['schools'] = school_serializer
    header['HTTP_X_CSTATUS'] = 0

    return Response(data, headers=header,status=HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_add(request):
    """학생 등록 api"""

    student_data = {}

    student_data['school_fk'] = request.POST.get('school_fk','')
    student_data['student_name'] = request.POST.get('student_name', '')
    student_data['grade'] = request.POST.get('grade', '')
    student_data['grade_class'] = request.POST.get('grade_class', '')
    student_data['student_number'] = request.POST.get('student_number', '')
    student_data['village'] = request.POST.get('village', '')
    student_data['gender'] = request.POST.get('gender', '')
    student_data['date_of_birth'] = request.POST.get('date_of_birth', '')
    student_data['medical_insurance_number'] = request.POST.get('medical_insurance_number', '')
    student_data['contact'] = request.POST.get('contact', '')
    student_data['parents_name'] = request.POST.get('parents_name', '')


    print(student_data)

    #student_data = request.POST.get('info','')
    #student_data = json.loads(request.body)
    #print(student_data)
    #print(student_data)
    #student_data = json.loads(student_data)
    #student_data = student_data['info']

    file_data = request.FILES.get('file','')

    if file_data:
        student_data['pic'] =file_data

    data = {}
    header = {}

    """학생뿐만 아니라 졸업생역시 min이 중복되는지여부 체크해야함."""
    if Student.objects\
            .filter(medical_insurance_number=student_data['medical_insurance_number'])\
            .exists():

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_409_CONFLICT)


    student_obj = AddStudentSerializer(data=student_data,partial=True)
    if student_obj.is_valid():
         student_obj.save()
    else:
        #data['status'] = 2
        header['HTTP_X_CSTATUS'] = 2
        print(student_obj.errors)
        print("Student Enrollment Failed")
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    log(request,typ='Add Student',
        content='Insert Student ' +
                request.META.get('HTTP_USER_ID',''))
    #data['status'] = 0
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)





@api_view(['GET'])
@permission_classes([AllAuthenticated])
def student_get(request,student_id):

    """학생 수정시 학생 정보 로딩 api"""


    data = {}
    header = {}

    if student_id is None:
        #data['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    student_obj = Student.objects.select_related('school_fk').filter(student_id=student_id).\
        values('student_name', 'grade', 'grade_class', 'gender', 'date_of_birth', 'student_number', 'village', 'contact',
               'parents_name', 'school_fk__school_name')

    #print(student_serializer)


    data['info'] = student_obj

    header['HTTP_X_CSTATUS'] = 0
    print("student_detail")
    print(data)
    return Response(data,headers=header, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def student_get_img(request,student_id):

    "학생 수정시 학생 이미지 로딩 api"

    data = {}
    header = {}

    if student_id is None:
        #data['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    student_pic = Student.objects.get(student_id=student_id).pic
    if student_pic is None:
        header['HTTP_X_CSTATUS'] = 0
        return Response(headers=header,status=HTTP_200_OK)

    return FileResponse(student_pic,headers=header,status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def min_check(request):

    """min 중복여부 체크 api"""
    request = json.loads(request.body)
    min = request.get('min','')

    data = {}
    header = {}
    if not min:
        #data['status'] = 1
        header['status'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)




    """학생뿐만 아니라 졸업생역시 min이 중복되는지여부 체크해야함."""
    if Student.objects\
            .filter(medical_insurance_number=min)\
            .exists():
        data['check'] = False
    else:
        data['check'] = True

    #data['status'] = 0
    header['status'] = 0

    return Response(data,headers=header,status=HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([AllAuthenticated])
def student_modify(request):

    """학생 정보 수정시 사용 api"""

    student_data = {}
    student_data['student_id'] = request.POST.get('student_id','')
    student_data['school_fk'] = request.POST.get('school_fk','')
    student_data['student_name'] = request.POST.get('student_name','')
    student_data['grade'] = request.POST.get('grade','')
    student_data['grade_class'] = request.POST.get('grade_class','')
    student_data['student_number'] = request.POST.get('student_number', '')
    student_data['village'] = request.POST.get('village', '')
    student_data['gender'] = request.POST.get('gender', '')
    student_data['date_of_birth'] = request.POST.get('date_of_birth', '')
    student_data['medical_insurance_number'] = request.POST.get('medical_insurance_number', '')
    student_data['contact'] = request.POST.get('contact', '')
    student_data['parents_name'] = request.POST.get('parents_name', '')

    #student_data = request.POST.get('info','')
    #student_data = json.loads(student_data)
    print(student_data)
    file_data = request.FILES.get('file','')

    header = {}
    if file_data:
        student_data['pic'] = file_data

    student_id = student_data.pop('student_id')

    try:
        student_obj = Student.objects.get(medical_insurance_number=student_data['medical_insurance_number'])

    except:
        #data = {}
        #data['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)




    origin_img = student_obj.pic


    student_serializer = AddStudentSerializer(student_obj,data=student_data,partial=True)

    try:
        if student_serializer.is_valid():
            student_serializer.save()

            """이미지를 새로 갱신한다면 원래 이미지는 삭제 """
            if file_data and os.path.isfile(origin_img.path):
                os.remove(origin_img.path)
    except:
        #data ={}
        #data['status'] = 2
        header['HTTP_X_CSTATUS'] = 2
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    log(request,typ='Update Student',
        content='Update Student ' +
                request.META.get('HTTP_USER_ID',''))


    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([AllAuthenticated])
def student_delete(request,student_id):

    """학생 정보 삭제 api"""

    header = {}

    if student_id is None:
        #data['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        print("student_id error")
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    try:
        student_obj = Student.objects.\
                        prefetch_related('checkup_set').\
                        get(student_id=student_id)
    except:
        #data['status']= 2
        header['HTTP_X_CSTATUS'] = 2
        print("student does not exist")
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    checkup_set = student_obj.checkup_set.all()




    graduate_obj = model_to_dict(student_obj)
    graduate_obj.pop('student_id')
    min = graduate_obj['medical_insurance_number']


    if graduate_obj['pic'] == None or graduate_obj['pic'] =='':
        graduate_obj.pop('pic')

    try:

        graduate_serializer = GraduateSerializer(data = graduate_obj,partial=True)

        if graduate_serializer.is_valid():

            with transaction.atomic():
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
        #data['status'] = 3
        header['HTTP_X_CSTATUS'] = 3
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    log(request,typ='Delete Student',
        content='Delete Student ' +
                request.META.get('HTTP_USER_ID',''))
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_delete_multi(request):

    """학생 정보 일괄 삭제 api"""
    request_json = json.loads(request.body)

    student_obj_list = Student.objects.\
                        prefetch_related('checkup_set').\
                        filter(student_id__in=request_json['student_list'])

    data = {}
    header = {}

    for student_obj in student_obj_list:

        checkup_set = student_obj.checkup_set.all()

        graduate_obj = model_to_dict(student_obj)
        graduate_obj.pop('student_id')
        min = graduate_obj['medical_insurance_number']

        if graduate_obj['pic'] == None or graduate_obj['pic']=='':
            graduate_obj.pop('pic')

        try:
            graduate_serializer = GraduateSerializer(data=graduate_obj,partial=True)

            if graduate_serializer.is_valid():
                with transaction.atomic():
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
            #data['status'] = 1
            header['HTTP_X_CSTATUS'] = 1
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)



    print(connection.queries)



    log(request,typ='Delete Student',
        content='Delete Student ' +
                request.META.get('HTTP_USER_ID',''))
    #data['status'] = 0
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)

# @api_view(['POST'])
# def insert(request):
#     file= request.FILES.get('file')
#     """commune 등록"""
#
#     df = pd.read_excel(file,engine='openpyxl')
#     print(df)
#     list = []
#     for i in df.index:
#         #print(i)
#         data = {}
#         for j,k in enumerate(df.columns):
#             if k =='Commune clinic (English)':
#                 data['commune_clinic'] = df.values[i][j]
#             if k =='District':
#                 data['district'] = df.values[i][j]
#
#         list.append(data)
#     print(len(list))
#
#     with transaction.atomic():
#         for temp in list:
#             commune = CommuneClinic()
#             commune.commune_clinic = temp['commune_clinic']
#             print(temp['district'])
#             district = District.objects.get(district=temp['district'])
#
#             commune.district_fk = district
#
#             commune.save()
#             print(commune)
#
#     return Response()

# @api_view(['POST'])
# def insert(request):
#     file= request.FILES.get('file')
#     """district 만 있는 area 등록"""
#
#     district_set = District.objects.all()
#
#     with transaction.atomic():
#         for district in district_set:
#             area = Area()
#             area.province_fk = Province.objects.get(province_id=2)
#             area.district_fk = district
#             area.save()
#
#
#     return Response()

# @api_view(['POST'])
# def insert(request):
#     file= request.FILES.get('file')
#     """district와 commune이 있는 area 등록"""
#
#     commune_set = CommuneClinic.objects.all()
#     with transaction.atomic():
#         for commune in commune_set:
#             area = Area()
#             area.province_fk = Province.objects.get(province_id=2)
#             area.district_fk = commune.district_fk
#             area.commune_clinic_fk = commune
#             area.save()
#
#
#     return Response()


# @api_view(['POST'])
# def insert(request):
#     file= request.FILES.get('file')
#     """학교 등록"""
#
#     df = pd.read_excel(file,engine='openpyxl')
#     #print(df)
#     list = []
#     for i in df.index:
#         #print(i)
#         data = {}
#         for j,k in enumerate(df.columns):
#             if k =='Commune clinic (English)':
#                 data['commune_clinic'] = df.values[i][j]
#                 print(data['commune_clinic'])
#             if k =='School name':
#                 data['School name'] = df.values[i][j]
#
#         list.append(data)
#     print(list)
#     print(len(list))
#
#     with transaction.atomic():
#         for temp in list:
#             school = School()
#             commune = CommuneClinic.objects.get(commune_clinic=temp['commune_clinic'])
#             school.school_name = temp['School name']
#             area = Area.objects.get(commune_clinic_fk=commune)
#
#             school.area_fk = area
#             print(school.area_fk)
#             school.save()
#             print(school)
#
#     return Response()

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def student_addAll(request):

    """학생 일괄 등록 excel 파일 파싱 후 저장"""

    file = request.FILES.get('file','')

    res = {}
    header = {}
    if not file:
        res['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    print(file)
    file_check = str(file)


    file_check = file_check.split('.')

    if file_check[-1] =='xlsx':
        df = pd.read_excel(file,engine='openpyxl')
    else:
        df = pd.read_excel(file)



    #df = df.drop(['No'],axis=1)
    print("df")
    print(df)
    school_id_list = list(set(df['School ID']))
    print("school_id list")
    print(school_id_list)
    df = df.rename({})
    for school_id in school_id_list:
        school_fk = School.objects.filter(school_id=school_id).values('id').first()
        #print(connection.queries)

        df['School ID'] = df['School ID'].apply(lambda x:school_fk['id'] if x==school_id else x)

    print("test 지점")

    df.columns = ['school_fk','student_id','student_name',
                  'grade','grade_class','student_number','date_of_birth',
                  'gender','medical_insurance_number','village','contact','parents_name']
    df = df.replace(np.NAN,'')
    df['gender'] = df['gender'].replace({'Nam': 'm', 'Nữ': 'f'})
    print("df test 22")
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
                data[k] = datetime.datetime.strptime(df.values[i][j],"%Y-%m-%d").date()

            else:
                data[k] = df.values[i][j]
        if data['medical_insurance_number'] not in list(Student.objects.values_list('medical_insurance_number', flat=True)):
            student_obj = AddStudentSerializer(data=data,partial=True)

            if student_obj.is_valid():
                student_obj.save()
            else:
                print(student_obj.errors)




    log(request,typ='Upload Student',
        content='Upload Student file')

    res['status'] = 0
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)