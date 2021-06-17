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
def student_add(request):
    """학생 등록 api"""

    student_data = json.loads(request.body)


    data = {}
    header = {}

    """학생뿐만 아니라 졸업생역시 min이 중복되는지여부 체크해야함."""
    if Student.objects\
            .filter(medical_insurance_number=student_data['medical_insurance_number'])\
            .exists() or \
            Graduate.objects.\
                    filter(medical_insurance_number=student_data['medical_insurance_number'])\
                    .exists():

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_409_CONFLICT)


    student_obj = AddStudentSerializer(data=student_data,partial=True)
    if student_obj.is_valid():
         student_obj.save()
    else:
        #data['status'] = 2
        header['HTTP_X_CSTATUS'] = 2
        print("Student Enrollment Failed")
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def students_add(request):
    """학생 배치 등록 api"""

    student_data = json.loads(request.body)

    header = {}


    for student in student_data:
        student_obj = AddStudentSerializer(data=student,partial=True)

        if student_obj.is_valid():
            student_obj.save()
        else:
            print(student_obj.errors)

    header['HTTP_X_CSTATUS'] = 0
    return Response(headers=header,status=HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def min_check(request):

    """min 중복여부 체크 api"""

    min = request.GET.get('min','')
    data = {}
    header = {}
    if not min:
        #data['status'] = 1
        header['status'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)




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

    #data['status'] = 0
    header['status'] = 0

    return Response(data,headers=header,status=HTTP_200_OK)



