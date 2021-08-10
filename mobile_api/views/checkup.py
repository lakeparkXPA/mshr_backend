from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.status import *
import json
import jwt

from mobile_api.permissions import *
from mobile_api.serializers import *
from mobile_api.models import User
from mshr_backend.settings import ALGORITHM, SECRET_KEY, BASE_DIR
import datetime




@api_view(['POST'])
@permission_classes([AllAuthenticated])
def edit_items(request):
    """examination results 일괄 등록"""

    request = json.loads(request.body)


    for checkup in request:
        # if Checkup.objects.filter(student_fk=
        #                   checkup['student_id']
        #                     ,date=datetime.datetime.today().strftime("%Y-%m-%d")).exists():

        if Checkup.objects.select_related('student_fk')\
            .filter(student_fk__medical_insurance_number=checkup['min']
                    ,date=datetime.datetime.today().strftime("%Y-%m-%d")).exists():

            # instance = Checkup.objects.filter(student_fk
            #                                   =checkup['student_id']
            #                                   ,date=datetime.datetime.today().strftime("%Y-%m-%d")).get()
            instance = Checkup.objects.select_related('student_fk')\
                        .filter(student_fk__medical_insurance_number=checkup['min']
                                ,date=datetime.datetime.today().strftime("%Y-%m-%d")).get()
            print("test")

        else:
            instance = Checkup()
            instance.date = datetime.datetime.today().strftime("%Y-%m-%d")
            instance.student_fk = Student.objects.get(medical_insurance_number =checkup['min'])

        checkup_serializer = AddCheckUpSerializer(instance=instance,data=checkup,partial=True)

        if checkup_serializer.is_valid():
            checkup_serializer.save()


    header = {}
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def edit_item(request):
    """edit one item"""

    request = json.loads(request.body)

    if Checkup.objects.select_related('student_fk') \
            .filter(student_fk__medical_insurance_number=request['min']
        , date=datetime.datetime.today().strftime("%Y-%m-%d")).exists():

        instance = Checkup.objects.select_related('student_fk') \
            .filter(student_fk__medical_insurance_number=request['min']
                    , date=datetime.datetime.today().strftime("%Y-%m-%d")).get()

    else:
        instance = Checkup()
        instance.date = datetime.datetime.today().strftime("%Y-%m-%d")
        instance.student_fk = Student.objects.get(medical_insurance_number=request['min'])

    checkup_serializer = AddCheckUpSerializer(instance=instance, data=request, partial=True)

    if checkup_serializer.is_valid():
        checkup_serializer.save()
    else:
        header = {}
        header['HTTP_X_CSTATUS'] = 0
        return Response(headers=header, status=HTTP_201_CREATED)

    header = {}
    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)