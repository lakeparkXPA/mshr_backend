from admin_api.models import *
from django.db.models import Q, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import permissions

from admin_api.package.log import log
from admin_api.permissions import *

import bcrypt
import string
import random

level_dic = {
    'Project BOM Manager': 0,
    'MoH': 0,
    'MoET': 0,
    'DoH': 1,
    'DoET': 1,
    'District Health Center': 2,
    'District DoET': 2,
    'Commune Clinic': 3,
    'School Staff': 4
}


@api_view(['POST'])
@permission_classes((IsMaster,))
def user_lst(request):
    print("user list 호출")
    try:
        try:
            user_id = request.data['user_id']
            user_level = User.objects.get(user_id__exact=user_id).user_level
        except:
            raise ValueError(1)

        search = request.data['search']
        print("서치: " + search)



        if user_level == 0:
            area_id = Area.objects.values('area_id')
        elif user_level == 1:
            area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
            area_id = Area.objects.filter(Q(province_fk__exact=area) & Q(district_fk__isnull=False)).\
                values('area_id')
        else:
            raise ValueError(2)

        users = User.objects.filter(area_fk__in=area_id).select_related('area_fk').select_related('school_fk')

        users_replace = users.extra(select={'school_fk': "coalesce(school_fk, '')",
                                            'school_name': "coalesce(school.school_name, '')",
                                            'email_address': "coalesce(user.email_address, '')",
                                            'user_mobile': "coalesce(user_mobile, '')"})

        users_select = users_replace.values('user_id',
                                            'user_name',
                                            'email_address',
                                            'user_tel',
                                            'user_mobile',
                                            'user_group',
                                            school_name=F('school_fk__school_name'))

        # if search:
        #     users_filter = users_select.filter(Q(school_name__contains=search)).exclude(id__isnull=True)
        # else:
        #     users_filter = users_select.exclude(id__isnull=True)

        if search:
            users_filter = users_select.filter(Q(user_name__contains=search)).exclude(id__isnull=True)
        else:
            users_filter = users_select.exclude(id__isnull=True)
        res = Response(users_filter, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['GET'])
@permission_classes((IsMaster,))
def user_check(request):
    user_id = request.GET.get('user_id', '')

    try:
        if not user_id:
            raise ValueError(1)
        try:
            id_cnt = User.objects.get(user_id__exact=user_id)
            raise ValueError(3)
        except User.DoesNotExist:
            res = Response(status=HTTP_200_OK)
            res['HTTP_X_CSTATUS'] = 0
            return res
    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['POST'])
@permission_classes((IsMaster,))
def user_add(request):

    request_json = json.loads(request.body)
    province = request_json.get('province','')
    district = request_json.get('district','')
    commune_clinic = request_json.get('commune_clinic','')
    school_name = request_json.get('school_name','')
    user_group = request_json.get('user_group','')
    user_level = level_dic[user_group]

    user_insert = User()
    user_insert.user_id = request_json.get('user_id')
    user_insert.password = bcrypt.hashpw(request_json.get('user_id').encode('utf-8'), bcrypt.gensalt(5)).decode('utf-8')
    user_insert.user_name = request_json.get('user_name','')
    user_insert.user_tel = request_json.get('user_tel','')
    user_insert.user_group = user_group
    user_insert.user_level = user_level

    if request.data['email_address']:
        user_insert.email_address = request.data['email_address']
    if request.data['user_mobile']:
        user_insert.user_mobile = request.data['user_mobile']

    if user_level == 0:
        area_id = Area.objects.filter(
            Q(province_fk__isnull= True) &
            Q(district_fk__isnull= True) &
            Q(commune_clinic_fk__isnull= True)
        ).first()

        user_insert.area_fk = area_id

    elif user_level == 1:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province)
        ).exclude(district_fk__isnull=False).first()

        user_insert.area_fk = area_id

    elif user_level == 2:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district)
        ).exclude(commune_clinic_fk__isnull=False).first()

        user_insert.area_fk = area_id

    elif user_level == 3:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district) &
            Q(commune_clinic_fk__commune_clinic__exact=commune_clinic)
        ).first()

        user_insert.area_fk = area_id

    else:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district) &
            Q(commune_clinic_fk__commune_clinic__exact=commune_clinic)
        ).first()

        school_fk = School.objects.filter(school_name__exact=school_name).first()
        user_insert.area_fk = area_id
        user_insert.school_fk = school_fk

    user_insert.save()
    # TODO---- Enable block later
    log(request, typ='Add user', content='Insert user ' + request_json.get('user_id'))

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['GET'])
@permission_classes((IsMaster,))
def reset_pw(request):
    user_id = request.GET.get('user_id')
    try:
        user_pk = User.objects.get(user_id__exact=user_id).id
        if user_id:
            string_pool = string.ascii_lowercase + string.digits
            password = ''
            for i in range(10):
                password += random.choice(string_pool)

            user_pw = User.objects.get(id=user_pk)
            user_pw.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(5)).decode('utf-8')
            user_pw.save()

            # TODO---- Enable block later
            log(request, typ='Reset password', content='Update password ' + user_id)
            pas = {"password": password}
            res = Response(pas, status=HTTP_200_OK)
            res['HTTP_X_CSTATUS'] = 0
            return res
        else:
            raise ValueError(1)

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def user_detail(request):
    user_id = request.GET.get('user_id')
    try:
        user = User.objects.filter(user_id__exact=user_id).select_related('area_fk').select_related('school_fk')
    except:
        data['status'] = 1
        return Response(data, status=HTTP_400_BAD_REQUEST)

    user_replace = user.extra(select={'user_mobile': "coalesce(user_mobile, '')",
                                      'email_address': "coalesce(user.email_address, '')",
                                      'province': "coalesce(province.province, '')",
                                      'district': "coalesce(district.district, '')",
                                      'commune_clinic': "coalesce(commune_clinic.commune_clinic, '')",
                                      'school_name': "coalesce(school.school_name, '')"})

    user_select = user_replace.values('user_id',
                                      'user_name',
                                      'email_address',
                                      'user_group',
                                      'user_tel',
                                      'user_mobile',
                                      school_name=F('school_fk__school_name'),
                                      province=F('area_fk__province_fk__province'),
                                      district=F('area_fk__district_fk__district'),
                                      commune_clinic=F('area_fk__commune_clinic_fk__commune_clinic')).first()
    res = Response(user_select, status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['PUT'])
@permission_classes((IsMaster,))
def user_edit(request):
    user_id = request.data['user_id']
    province = request.data['province']
    district = request.data['district']
    commune_clinic = request.data['commune_clinic']
    school_name = request.data['school_name']
    user_group = request.data['user_group']
    user_level = level_dic[user_group]

    user_pk = User.objects.get(user_id__exact=user_id).id
    user_insert = User.objects.get(id=user_pk)
    user_insert.user_id = user_id
    user_insert.user_name = request.data['user_name']
    user_insert.user_tel = request.data['user_tel']

    if request.data['email_address']:
        user_insert.email_address = request.data['email_address']
    if request.data['user_mobile']:
        user_insert.user_mobile = request.data['user_mobile']



    user_insert.user_group = user_group
    user_insert.user_level = user_level

    if user_level == 0:
        pass

    elif user_level == 1:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province)
        ).exclude(district_fk__isnull=False).first()

        user_insert.area_fk = area_id

    elif user_level == 2:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district)
        ).exclude(commune_clinic_fk__isnull=False).first()

        user_insert.area_fk = area_id

    elif user_level == 3:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district) &
            Q(commune_clinic_fk__commune_clinic__exact=commune_clinic)
        ).first()

        user_insert.area_fk = area_id

    else:
        area_id = Area.objects.filter(
            Q(province_fk__province__exact=province) &
            Q(district_fk__district__exact=district) &
            Q(commune_clinic_fk__commune_clinic__exact=commune_clinic)
        ).first()

        school_fk = School.objects.filter(school_name__exact=school_name).first()
        user_insert.area_fk = area_id
        user_insert.school_fk = school_fk

    user_insert.save()
    # TODO---- Enable block later
    log(request, typ='update user', content='Update user ' + request.data['user_id'])

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res


@api_view(['DELETE', 'GET'])
@permission_classes((IsMaster,))
def user_remove(request, pk):
    try:
        user_pk = User.objects.get(user_id__exact=pk).id
        user_del = User.objects.get(id=user_pk)
        user_del.delete()
        # TODO---- Enable block later
        log(request, typ='Delete user', content='Delete user ' + str(pk))
        res = Response(status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res



