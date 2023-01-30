from admin_api.models import *
from django.db.models import Q, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import permissions

from admin_api.package.log import log
from admin_api.permissions import *


@api_view(['POST'])
@permission_classes((IsMaster,))
def school_lst(request):
    try:
        try:
            user_id = request.data['user_id']
        except:
            raise ValueError(1)

        search = request.data['search']


        user_level = User.objects.get(user_id__exact=user_id).user_level

        if user_level == 0:
            area_id = Area.objects.values('area_id')
        elif user_level == 1:
            area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
            area_id = Area.objects.filter(province_fk__exact=area).values('area_id')
        else:
            raise PermissionError(2)


        schools = School.objects.filter(area_fk__in=area_id).select_related('area_fk')

        schools_replace = schools.extra(select={'remarks': "coalesce(remarks, '')"})

        schools_select = schools_replace.values('school_id',
                                                'school_name',
                                                'address',
                                                'staff_tel',
                                                'remarks',
                                                province=F('area_fk__province_fk__province'),
                                                district=F('area_fk__district_fk__district'),
                                                commune_clinic=F('area_fk__commune_clinic_fk__commune_clinic'))

        if search:
            schools_filter = schools_select.filter(Q(school_name__contains=search)).exclude(id__isnull=True)
        else:
            schools_filter = schools_select.exclude(id__isnull=True)

        res = Response(schools_filter, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['GET'])
@permission_classes((IsMaster,))
def school_check(request):
    school_id = request.GET.get('school_id', '')

    try:
        if not school_id:
            raise ValueError(3)
        try:
            id_cnt = School.objects.get(school_id__exact=school_id)
            raise ValueError(4)
        except School.DoesNotExist:
            res = Response(status=HTTP_200_OK)
            res['HTTP_X_CSTATUS'] = 0
            return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['POST'])
@permission_classes((IsMaster,))
def school_add(request):
    area_id = Area.objects.select_related('province_fk').select_related('district_fk'). \
        select_related('commune_clinic_fk').filter(
        Q(province_fk__province__exact=request.data['province']) &
        Q(district_fk__district__exact=request.data['district']) &
        Q(commune_clinic_fk__commune_clinic__exact=request.data['commune_clinic'])
    ).first()

    school = School()
    school.area_fk = area_id
    school.school_id = request.data['school_id']
    school.school_name = request.data['school_name']
    school.agency_category = request.data['agency_category']
    school.address = request.data['address']
    school.staff_tel = request.data['staff_tel']

    if request.data['director']:
        school.director = request.data['director']
    if request.data['email_address']:
        school.email_address = request.data['email_address']
    if request.data['commune_center_tel']:
        school.commune_center_tel = request.data['commune_center_tel']
    if request.data['department_head_tel']:
        school.department_head_tel = request.data['department_head_tel']
    if request.data['remarks']:
        school.remarks = request.data['remarks']


    school.save()
    # TODO---- Enable block later
    log(request, typ='Add school', content='Insert school ' + str(request.data['school_id']))

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['GET'])
@permission_classes((IsMaster,))
def school_detail(request):
    school_id = request.GET.get('school_id')
    schools = School.objects.filter(school_id__exact=school_id).select_related('area_fk')

    schools_replace = schools.extra(select={'remarks': "coalesce(remarks, '')",
                                            'email_address': "coalesce(email_address, '')",
                                            'commune_center_tel': "coalesce(commune_center_tel, '')",
                                            'department_head_tel': "coalesce(department_head_tel, '')",
                                            'director': "coalesce(director, '')"})

    schools_select = schools_replace.values('school_id',
                                            'school_name',
                                            'agency_category',
                                            'address',
                                            'director',
                                            'email_address',
                                            'commune_center_tel',
                                            'department_head_tel',
                                            'staff_tel',
                                            'remarks',
                                            province=F('area_fk__province_fk__province'),
                                            district=F('area_fk__district_fk__district'),
                                            commune_clinic=F('area_fk__commune_clinic_fk__commune_clinic')).first()

    res = Response(schools_select, status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['PUT'])
@permission_classes((IsMaster,))
def school_edit(request):

    print(request.data)
    area_id = Area.objects.select_related('province_fk').select_related('district_fk'). \
        select_related('commune_clinic_fk').filter(
        Q(province_fk__province__exact=request.data['province']) &
        Q(district_fk__district__exact=request.data['district']) &
        Q(commune_clinic_fk__commune_clinic__exact=request.data['commune_clinic'])
    ).first()
    school_pk = School.objects.get(school_id__exact=request.data['school_id']).id

    school = School.objects.get(id=school_pk)
    school.area_fk = area_id
    school.school_id = request.data['school_id']
    school.school_name = request.data['school_name']
    school.agency_category = request.data['agency_category']
    school.address = request.data['address']
    school.staff_tel = request.data['staff_tel']

    if request.data['director']:
        school.director = request.data['director']
    if request.data['email_address']:
        school.email_address = request.data['email_address']
    if request.data['commune_center_tel']:
        school.commune_center_tel = request.data['commune_center_tel']
    if request.data['department_head_tel']:
        school.department_head_tel = request.data['department_head_tel']
    if request.data['remarks']:
        school.remarks = request.data['remarks']

    school.save()
    # TODO---- Enable block later
    log(request, typ='Update school', content='Update school ' + str(request.data['school_id']))

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['DELETE', 'GET'])
@permission_classes((IsMaster,))
def school_remove(request, pk):

    try:
        school_pk = School.objects.get(school_id__exact=pk).id
        school_del = School.objects.get(id=school_pk)
        school_del.delete()
        # TODO---- Enable block later
        log(request, typ='Delete school', content='Delete school ' + str(pk))
        res = Response(status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res

