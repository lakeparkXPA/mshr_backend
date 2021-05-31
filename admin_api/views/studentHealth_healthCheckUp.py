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

    school_id = request.POST.get('school_id','')
    start_date = request.POST.get('start_date','')
    end_date = request.POST.get('end_date','')
    checked = request.POST.get('checked','')
    grade = request.POST.get('grade','')
    name = request.POST.get('name','')



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
        raise exceptions.ValidationError(str(e))
    #print(checkup)



    checkup_serializer = CheckUpSerializer(checkup,many=True)

    data = {}
    data['checkUpList'] = checkup_serializer.data

    print(connection.queries)
    #print(checkup)

    return Response(data,status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def stuList(request):

    """체크업 등록시 학생 정보 조회"""

    school_id = request.POST.get('school_id','')
    grade = request.POST.get('grade','')


    q = Q()

    if school_id =='':
        raise exceptions.ValidationError("inValid school_id")
    else:
        q.add(Q(school_fk=school_id),Q.AND)

    if grade:
        q.add(Q(grade=grade),Q.AND)

    try:

        students_obj = Student.objects.filter(q)

    except Exception as e:
        raise exceptions.ValidationError(str(e))

    students_serializer = StudentListSerializer(students_obj,many=True).data

    data = {}

    data['students'] = students_serializer

    return Response(data,status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllAuthenticated])
def addCheckUp(request):
    """빈 체크업 등록 페이지"""

    student_id = request.POST.get('student_id','')

    """같은날 체크업은 1개만 등록"""
    if student_id == '':
        raise exceptions.ValidationError("inValid student_id")
    else:
        try:
            """체크업은 개인당 하루에 최대 1개"""
            if Checkup.objects\
                .filter(student_fk=student_id,
                        date=datetime.datetime.today().strftime("%Y-%m-%d"))\
                        .exists():
                raise ValueError("Already exist check up.")

            student = Student.objects.get(student_id=student_id)

            checkup = Checkup(student_fk=student,date=datetime.datetime.today().strftime("%Y-%m-%d"))

            checkup.save()

        except Exception as e:
            raise exceptions.ValidationError(str(e))


    #log(request,typ='Add Health Check-up',
     #   content='Insert Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))
    return Response(status=HTTP_201_CREATED)




@api_view(['POST'])
@permission_classes([AllAuthenticated])
def modiCheckUp(request):
    """체크업 수정 api"""

    checkup_data = request.POST.get('info','')
    print(checkup_data)
    checkup_data = json.loads(checkup_data)

    try:
        checkup_obj = Checkup.objects.get(id=checkup_data['id'])

        checkup_serilizer = CheckUpSerializer(checkup_obj,data=checkup_data,partial=True)

        if checkup_serilizer.is_valid():
            checkup_serilizer.save()
        else:
            raise exceptions.ValidationError("Cannot update checkup data")

    except Exception as e:
        raise exceptions.ValidationError(str(e))



    #log(request,typ='Update Health Check-up',
     #   content='Update Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))
    return Response(status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def getCheckUp(request):
    """체크업 상세 조회 api"""
    school_id = request.POST.get('school_id','')
    student_id = request.POST.get('student_id','')
    checkup_id = request.POST.get('checkup_id','')


    data ={}
    if checkup_id:
        try:
            checkup_obj = Checkup.objects.select_related('student_fk')\
                            .get(id=checkup_id)

            checkup_serializer = CheckUpGetSerializier(checkup_obj).data

            data = checkup_serializer

        except:
            raise exceptions.ValidationError("Does not exist checkup.")

    else:
        raise exceptions.ValidationError("check up id error.")




    return Response(data,status=HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllAuthenticated])
def delCheckUp(request,checkup_id):
    """체크업 삭제 api"""


    try:
        checkup_obj = Checkup.objects.get(id=checkup_id)

        checkup_obj.delete()
    except:
        raise exceptions.ValidationError("can't not delete check up.")

    #log(request,typ='Delete Health Check-up',
     #   content='Delete Health Check-up ' +
      #          request.META.get('HTTP_USER_ID', ''))

    return Response(status=HTTP_200_OK)