from django.db.models import Q
from django.http import FileResponse, JsonResponse
import datetime
from rest_framework.decorators import *

from rest_framework.status import *
from django.db.models import Count
from admin_api.permissions import *
from admin_api.serializers import *

from mshr_backend.settings import STATIC_DIR
from admin_api.custom import *
from django.db import connection
import json

@api_view(['POST'])
@permission_classes([AllAuthenticated])
def dashboard_info(request):
    """
    대시보드 건강검진 현황 조회 및 차트
    """
    print("대시보드 info method 테스트")
    request = json.loads(request.body)
    header = {}
    print(request)
    user_id = request.get('user_id','')
    province = request.get('province','')
    district = request.get('district','')
    commune = request.get('commune','')
    school_id = request.get('school_id','')
    start_date = request.get('start_date','')
    end_date = request.get('end_date','')

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")\
                                    .strftime("%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")\
                                    .strftime("%Y-%m-%d")

    data = {}
    q = Q()

    if province:
        q.add(Q(student_fk__school_fk__area_fk__province_fk__province=province),q.AND)
    if district:
        q.add(Q(student_fk__school_fk__area_fk__district_fk__district=district),q.AND)
    if commune:
        q.add(Q(student_fk__school_fk__area_fk__commune_clinic_fk__commune_clinic=commune),q.AND)
    if school_id:
        q.add(Q(student_fk__school_fk__id=school_id),q.AND)

    if start_date and end_date:
        q.add(Q(date__range=[start_date,end_date]),q.AND)

    q.add(Q(graduate_fk=None),Q.AND)

    """필터링 조건 """
    checkup_set = Checkup.objects.select_related('student_fk').\
                    select_related('student_fk__school_fk').\
                    select_related('student_fk__school_fk__area_fk').\
                    select_related('student_fk__school_fk__area_fk__province_fk').\
                    select_related('student_fk__school_fk__area_fk__district_fk').\
                    select_related('student_fk__school_fk__area_fk__commune_clinic_fk').filter(q)

    """건강검진받은 전체 인원"""
    print(checkup_set.count())

    data['total_count'] = checkup_set.count()
    progress_check = Q()

    """건강검진 완료 여부 체크 항목 corrected는 항상 null일수 있으므로 체크항목에서 제외"""

    progress_check.add(Q(height__isnull=True) |
                       Q(weight__isnull=True) |
                       Q(vision_left__isnull=True) |
                       Q(vision_right__isnull=True)|
                       Q(glasses__isnull=True)|
                       Q(dental__isnull=True)|
                       Q(hearing__isnull=True)|
                       Q(systolic__isnull=True)|
                       Q(diastolic__isnull=True)|
                       Q(bust__isnull=True),q.OR)


    data['progress_count'] = checkup_set.filter(progress_check).count()

    data['completed_count']= data['total_count'] - data['progress_count']

    #print(checkup_set.filter(progress_check).count())



    """hc_grade"""

    grade = {}


    for i in range(1,10):
        gender = {}
        gender["male"] = 0
        gender["female"] = 0
        grade["grade_{}".format(i)] = gender


    for checkup in checkup_set:
        student = checkup.student_fk

        if student.gender == 'Nam':
            grade["grade_{}".format(student.grade)]["male"]+=1
        elif student.gender =='Nữ':
            grade["grade_{}".format(student.grade)]["female"] += 1

    data['hc_grade'] = grade
    print(grade)


    """hc_item"""
    item = {}
    item["height"] = checkup_set.exclude(height__isnull=True).count()
    item["weight"] = checkup_set.exclude(weight__isnull=True).count()
    item["vision"] = checkup_set.exclude(vision_left__isnull=True,
                                         vision_right__isnull=True).count()
    item["hearing"] = checkup_set.exclude(hearing__isnull=True).count()
    item["bp"] = checkup_set.exclude(systolic__isnull=True,
                                     diastolic__isnull=True).count()
    item["chest"] = checkup_set.exclude(bust__isnull=True).count()
    item["dental"] = checkup_set.exclude(dental__isnull=True).count()
    data['hc_items'] = item



    """average weight"""
    print("weight test 시작")
    weight = {}
    temp = {}

    for i in range(1,10):
        gender = {}

        gender["male"] = 0
        gender["female"] = 0
        weight["grade_{}".format(i)] = gender


        sum = {}
        sum["male"] = {"total":0,"count":0}
        sum["female"] = {"total": 0, "count": 0}

        temp["grade_{}".format(i)] = sum




    for checkup in checkup_set:
        student = checkup.student_fk

        if student.gender == 'Nam' and checkup.weight != None:
            temp["grade_{}".format(student.grade)]["male"]["total"]+=checkup.weight
            temp["grade_{}".format(student.grade)]["male"]["count"]+=1
            #weight["grade_{}".format(student.grade)]["male"]+=checkup.weight
        elif student.gender =='Nữ' and checkup.weight != None:

            temp["grade_{}".format(student.grade)]["female"]["total"] += checkup.weight
            temp["grade_{}".format(student.grade)]["female"]["count"] += 1
            #weight["grade_{}".format(student.grade)]["female"] +=checkup.weight

    for i in range(1,10):
        if temp["grade_{}".format(i)]["male"]["count"] !=0:
            weight["grade_{}".format(i)]["male"] =(temp["grade_{}".format(i)]["male"]["total"])/(temp["grade_{}".format(i)]["male"]["count"])
        if temp["grade_{}".format(i)]["female"]["count"] !=0:
            weight["grade_{}".format(i)]["female"]= (temp["grade_{}".format(i)]["female"]["total"]) / (temp["grade_{}".format(i)]["female"]["count"])

    print("weight")
    print(weight)
    data['average_weight'] = weight

    """average height"""

    height = {}
    temp = {}

    for i in range(1, 10):
        gender = {}

        gender["male"] = 0
        gender["female"] = 0
        height["grade_{}".format(i)] = gender

        sum = {}
        sum["male"] = {"total": 0, "count": 0}
        sum["female"] = {"total": 0, "count": 0}

        temp["grade_{}".format(i)] = sum

    for checkup in checkup_set:
        student = checkup.student_fk

        if student.gender == 'Nam' and checkup.height != None:
            temp["grade_{}".format(student.grade)]["male"]["total"] += checkup.height
            temp["grade_{}".format(student.grade)]["male"]["count"] += 1
            # weight["grade_{}".format(student.grade)]["male"]+=checkup.weight

        elif student.gender == 'Nữ' and checkup.height != None:
            temp["grade_{}".format(student.grade)]["female"]["total"] += checkup.height
            temp["grade_{}".format(student.grade)]["female"]["count"] += 1
            # weight["grade_{}".format(student.grade)]["female"] +=checkup.weight

    for i in range(1, 10):
        if temp["grade_{}".format(i)]["male"]["count"] != 0:
            height["grade_{}".format(i)]["male"] = (temp["grade_{}".format(i)]["male"]["total"]) / (
            temp["grade_{}".format(i)]["male"]["count"])
        if temp["grade_{}".format(i)]["female"]["count"] != 0:
            height["grade_{}".format(i)]["female"] = (temp["grade_{}".format(i)]["female"]["total"]) / (
            temp["grade_{}".format(i)]["female"]["count"])

    print("height")
    print(height)
    data['average_height'] = height
    #print(connection.queries)

    """grade_hc_items"""

    grade_hc_items = {}


    check_list = {"height":0,"weight":0,"vision":0,"hearing":0,"bp":0,"chest":0,"dental":0}

    for i in range(1,10):
        grade_hc_items["grade_{}".format(i)] = check_list


    for checkup in checkup_set:
        student = checkup.student_fk
        if checkup.weight != None:
            grade_hc_items["grade_{}".format(student.grade)]["weight"]+=1

        if checkup.height != None:
            grade_hc_items["grade_{}".format(student.grade)]["height"] += 1
        if checkup.vision_left != None and checkup.vision_right != None:
            grade_hc_items["grade_{}".format(student.grade)]["vision"] += 1

        if checkup.hearing != None:
            grade_hc_items["grade_{}".format(student.grade)]["hearing"]+=1

        if checkup.systolic != None and checkup.diastolic != None:
            grade_hc_items["grade_{}".format(student.grade)]["bp"] += 1
        if checkup.bust != None:
            grade_hc_items["grade_{}".format(student.grade)]["chest"] += 1

    data["grade_hc_items"] = grade_hc_items

    print("grade_hc_items")
    print(grade_hc_items)
    #data['status'] = 0

    header['HTTP_X_CSTATUS'] = 0

    #print(data)
    return Response(data,headers=header,status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllAuthenticated])
def dashboard_filter(request):
    '''
    대시보드 province, district,school 필터링
    '''

    print("대시보드 filter method 테스트")

    request = json.loads(request.body)
    header = {}

    filter = request.get('filter','')
    province = request.get('province','')
    district = request.get('district', '')
    commune = request.get('commune','')
    school = request.get('school_name', '')

    data = {}

    try:
        user_level = User.objects.get(user_id = request.get('user_id')).user_level
        print(user_level)

    except Exception as e:
        #data['status'] = 1 #유저 id 존재 x
        header['HTTP_X_CSTATUS'] =1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)





    if filter == 'province' and (user_level is 0):

        """Province 검색 할 경우"""
        print("filter테스트")
        try:
            province_list = Province.objects.all().values('province')
            data['province'] = []


            #raise exceptions.ValidationError(data)
            for order_list in province_list:

                data['province'].append(order_list['province'])
                print(order_list['province'])

        except:
            #data['status'] = 2
            header['HTTP_X_CSTATUS'] = 2
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)
            #raise exceptions.ValidationError(data)


    elif filter =='district' and (user_level in[0,1]):
        """district 검색 할 경우"""

        if not province:
            header['HTTP_X_CSTATUS'] = 2
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)


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
            header['HTTP_X_CSTATUS'] = 2
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)

        commune_obj = CommuneClinic.objects.select_related('district_fk').\
                        filter(district_fk__district=district)

        commune_list = CommuneSerializer(commune_obj,many=True).data
        print(connection.queries)
        data['commune'] = []

        for commune in commune_list:
            data['commune'].append(commune['commune_clinic'])





    elif filter == 'school' and (user_level in [0,1,2,3]):

        if not province or not district or not commune:
            header['HTTP_X_CSTATUS'] = 2
            return Response(headers=header,status=HTTP_400_BAD_REQUEST)


        school_obj = School.objects.select_related('area_fk').\
            select_related('area_fk__province_fk').\
            select_related('area_fk__district_fk').\
            select_related('area_fk__commune_clinic_fk').\
            filter(area_fk__province_fk__province=province,
                   area_fk__district_fk__district=district,
                   area_fk__commune_clinic_fk__commune_clinic=commune).values('school_id','school_name')

        data['schools'] = []

        for obj in school_obj:
            print(obj)
            school_info = {}

            school_info['school_name'] = obj['school_name']
            school_info['school_id'] =obj['school_id']

            data['schools'].append(school_info)



    #data['status'] = 0 #성공
    header['HTTP_X_CSTATUS'] = 0

    return JsonResponse(data,headers=header, status=HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice_list(request):
    """
    공지사항 list 조회 api
    """
    print("대시보드 공지사항조회 method 테스트")
    header = {}
    try:
        notice_list_obj = Notice.objects.all()
        notice_serializer = NoticeListSerializer(notice_list_obj,many=True)

        notice_list = {}
        notice_list['notice'] = notice_serializer.data
        notice_list['status'] = 0

    except:

        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)
        #raise exceptions.APIException(data)

    header['HTTP_X_CSTATUS'] = 0

    return Response(notice_list,headers=header,status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice(request,notice_id):


    """
    공지사항 상세조회 api
    """

    print("대시보드 공지사항 상세조회 method 테스트")
    header = {}
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
        header['HTTP_X_CSTATUS'] = 1
        return Response(headers=header,status=HTTP_400_BAD_REQUEST)


    #notice['status'] = 0
    header['HTTP_X_CSTATUS'] = 0

    return Response(notice,headers=header)


@api_view(['GET'])
@permission_classes([AllAuthenticated])
def dashboard_notice_img(request,notice_id):
    """
    공지사항 파일 다운로드 API
    """
    print("대시보드 공지사항 파일 다운로드 method 테스트")
    notice_file = NoticeFile.objects.get(notice_fk=notice_id).file_name
    if notice_file is None:
        return Response()

    header = {}
    header['HTTP_X_CSTATUS'] = 0

    return FileResponse(notice_file,headers=header,as_attachment=True)



