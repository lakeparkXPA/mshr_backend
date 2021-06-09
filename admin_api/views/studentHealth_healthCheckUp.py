import os

import datetime
from django.db.models import Q
from django.http import FileResponse, JsonResponse

from rest_framework.decorators import *

from rest_framework.status import *

from admin_api.permissions import *
from admin_api.serializers import *
from admin_api.package.log import *
from admin_api.custom import *
from django.db import connection
import pandas as pd
import json
from django.db import transaction



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def list(request):

    """체크업 리스트 조회 API"""
    request = json.loads(request.body)


    school_id = request.get('school_id','')
    start_date = request.get('start_date','')
    end_date = request.get('end_date','')
    checked = request.get('checked','')
    grade = request.get('grade','')
    name = request.get('name','')

    data = {}
    header = {}

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")\
                                    .strftime("%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")\
                                    .strftime("%Y-%m-%d")


    print(start_date,end_date)


    q = Q()
    if school_id:
        q.add(Q(student_fk__school_fk=school_id),q.AND)

    if grade and grade != 0:
        q.add(Q(student_fk__grade=grade),q.AND)

    if checked:
        q.add(Q(checked=checked),Q.AND)

    if name:
        q.add((Q(student_fk__medical_insurance_number=name) | Q(student_fk__student_name=name)),Q.AND)

    if start_date and end_date:
        q.add(Q(date__range=[start_date,end_date]),Q.AND)

    #q.add(Q(graduate_fk=None),Q.AND)
    try:
        checkup = Checkup.objects.select_related('student_fk').select_related('student_fk__school_fk').filter(q)

    except Exception as e:
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)
        #raise exceptions.ValidationError(data)
    #print(checkup)



    checkup_serializer = CheckUpSerializer(checkup,many=True)


    data['checkUpList'] = checkup_serializer.data

    print(connection.queries)
    #print(checkup)
    #data['status'] = 0
    header['HTTP_X_CSTATUS'] = 0
    return Response(data,headers=header,status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def stuList(request):

    """체크업 등록시 학생 정보 조회"""
    request = json.loads(request.body)

    school_id = request.get('school_id','')
    grade = request.get('grade','')


    q = Q()


    data = {}
    header = {}
    if school_id =='':

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)
        #raise exceptions.ValidationError(data)
    else:
        q.add(Q(school_fk=school_id),Q.AND)

    if grade:
        q.add(Q(grade=grade),Q.AND)

    try:

        students_obj = Student.objects.filter(q)

    except Exception as e:
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)

    students_serializer = StudentListSerializer(students_obj,many=True).data


    data['students'] = students_serializer
    #data['status'] = 0

    header['HTTP_X_CSTATUS'] = 0

    return Response(data,headers=header,status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def addCheckUp(request):
    """빈 체크업 등록 페이지"""

    request = json.loads(request.body)

    student_id = request.get('student_id','')

    data = {}
    header = {}
    """같은날 체크업은 1개만 등록"""
    if student_id == '':
        header['HTTP_X_CSTATUS'] =1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)

    else:

        """체크업은 개인당 하루에 최대 1개"""
        if Checkup.objects\
            .filter(student_fk=student_id,
                    date=datetime.datetime.today().strftime("%Y-%m-%d"))\
                    .exists():
            header['HTTP_X_CSTATUS'] = 2
            return Response(headers=header, status=HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)

        except:
            header['HTTP_X_CSTATUS'] = 1
            return Response(headers=header, status=HTTP_400_BAD_REQUEST)

        checkup = Checkup(student_fk=student,date=datetime.datetime.today().strftime("%Y-%m-%d"))

        checkup.save()



    #log(request,typ='Add Health Check-up',
     #   content='Insert Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))
    #data['status']=0
    header['HTTP_X_CSTATUS'] = 0

    return Response(data,headers=header,status=HTTP_201_CREATED)




@api_view(['POST'])
@permission_classes([AllAuthenticated])
def modiCheckUp(request):
    """체크업 수정 api"""

    request = json.loads(request.body)

    checkup_data = request.get('info','')
    print(checkup_data)


    data = {}
    header = {}
    try:
        checkup_obj = Checkup.objects.get(id=checkup_data['id'])

        checkup_serilizer = CheckUpSerializer(checkup_obj,data=checkup_data,partial=True)

        if checkup_serilizer.is_valid():
            checkup_serilizer.save()
        else:
            raise exceptions.ValidationError("Cannot update checkup data")

    except Exception as e:
        #data['status'] = 1
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)




    #log(request,typ='Update Health Check-up',
     #   content='Update Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))

    #data['status'] = 0

    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def getCheckUp(request):
    """체크업 상세 조회 api"""

    request = json.loads(request.body)

    school_id = request.get('school_id','')
    student_id = request.get('student_id','')
    checkup_id = request.get('checkup_id','')


    data ={}
    header = {}

    if checkup_id:
        try:
            checkup_obj = Checkup.objects.select_related('student_fk')\
                            .get(id=checkup_id)

            checkup_serializer = CheckUpGetSerializier(checkup_obj).data

            data['info'] = checkup_serializer

        except:
            #data['status']= 1
            print("Does not exist checkup.")

            header['HTTP_X_CSTATUS'] = 1
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    else:
        #data['status'] = 1
        print("check up id error")

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header, status=HTTP_400_BAD_REQUEST)




    header['HTTP_X_CSTATUS'] = 0
    return Response(data,headers=header,status=HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllAuthenticated])
def delCheckUp(request,checkup_id):
    """체크업 삭제 api"""


    data = {}
    header = {}

    try:
        checkup_obj = Checkup.objects.get(id=checkup_id)

        checkup_obj.delete()
    except:
        print("can't not delete check up.")

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)

    #log(request,typ='Delete Health Check-up',
     #   content='Delete Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))

    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def delChekUpMulti(request):
    """체크업 다중 삭제 Api"""

    request = json.loads(request.body)
    checkup_list = request['checkup_list']


    header = {}

    try:
        with transaction.atomic():
            for checkup in checkup_list:
                checkup_obj = Checkup.objects.get(id=checkup)
                checkup_obj.delete()
    except:

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)

    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_200_OK)

