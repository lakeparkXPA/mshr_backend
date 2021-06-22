from admin_api.models import *
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import permissions
from admin_api.permissions import *

@api_view(['POST'])
@permission_classes((IsMaster))
def log_lst(request):
    try:
        try:
            user_id = request.data['user_id']
        except:
            raise ValueError(1)

        search = request.data['search']

        user_level = User.objects.get(user_id__exact=user_id).user_level

        if user_level == 0:
            logs = Log.objects.extra(select={"ip": "coalesce(ip, '')"}).\
                values('id', 'user_id', 'user_name', 'log_time', 'log_type', 'log_content', 'ip')
        elif user_level == 1:
            area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
            area_id = Area.objects.filter(Q(province_fk__exact=area) & Q(district_fk__isnull=False)).\
                values('area_id')
            users = User.objects.filter(area_fk__in=area_id).values('id')
            logs = Log.objects.filter(user_fk__in=users).extra(select={"ip": "coalesce(ip, '')"}).\
                values('id', 'user_id', 'user_name', 'log_time', 'log_type', 'log_content', 'ip')
        else:
            raise PermissionError(2)

        if search:
            log_filter = logs.filter(Q(user_id__contains=search) |
                                     Q(user_name__contains=search) |
                                     Q(log_type__contains=search) |
                                     Q(log_content__contains=search) |
                                     Q(ip__contains=search))
        else:
            log_filter = logs

        res = Response(log_filter, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res