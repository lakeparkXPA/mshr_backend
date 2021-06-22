from admin_api.models import *
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework import permissions
from admin_api.permissions import *

@api_view(['GET'])
@permission_classes((AllAuthenticated))
def area_name(request):
    province = request.GET.get('province', '')
    district = request.GET.get('district', '')
    commune_clinic = request.GET.get('commune_clinic', '')

    if commune_clinic:
        area = Area.objects.filter(Q(province_fk__province__exact=province) &
                                   Q(district_fk__district__exact=district) &
                                   Q(commune_clinic_fk__commune_clinic__exact=commune_clinic)).values('area_id')
        return_dict = {'school_name': School.objects.filter(area_fk__in=area).values_list('school_name',
                                                                                          flat=True)}
    elif district:
        district_id = District.objects.get(district__exact=district)
        return_dict = {
            'commune_clinic':
                CommuneClinic.objects.filter(district_fk__exact=district_id).values_list('commune_clinic',
                                                                                         flat=True)}
    elif province:
        province_id = Province.objects.get(province__exact=province)
        return_dict = {'district': District.objects.filter(province_fk__exact=province_id).values_list('district',
                                                                                                       flat=True)}
    else:
        return_dict = {'province': Province.objects.values_list('province', flat=True)}

    res = Response(return_dict, status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res