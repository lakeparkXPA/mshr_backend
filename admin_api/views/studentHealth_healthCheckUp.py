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
import json
from django.db import transaction



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def studentHealth_healthCheckUp_list(request):

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
def studentHealth_healthCheckUp_stuList(request):

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