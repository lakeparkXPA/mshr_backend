
from django.http import FileResponse, JsonResponse

from rest_framework.decorators import *

from rest_framework.status import *

from admin_api.permissions import *
from admin_api.serializers import *

from mshr_backend.settings import STATIC_DIR
from admin_api.custom import *
from django.db import connection


@api_view(['POST'])
#@permission_classes([AllAuthenticated])
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
#@permission_classes([AllAuthenticated])
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
def dashboard_notice_img(request,notice_id):
    """
    공지사항 파일 다운로드 API
    """

    notice_file = NoticeFile.objects.get(notice_fk=notice_id).file_name
    if notice_file is None:
        return Response()

    return FileResponse(notice_file,as_attachment=True)



