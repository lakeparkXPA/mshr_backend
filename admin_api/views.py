from .models import *

from django.http import HttpResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.core import serializers
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def school_lst(request, format=None):
    try:
        try:
            user_id = request.data['user_id']
        except:
            raise ValueError('user id')

        try:
            search = request.data['search']
        except:
            raise ValueError('search')


        schools = User.objects.select_related('School').select_related('Area').select_related('Province').\
            select_related('District').select_related('CommuneClinic').only(['school_fk__school_id',
                                                                             'school_fk__school_name',
                                                                             'area_fk__province_fk__province',
                                                                             'area_fk__district_fk__district',
                                                                             'area_fk__commune_clinic_fk__commune_clinic',
                                                                             'school_fk__address',
                                                                             'school_fk__staff_tel',
                                                                             'school_fk__remarks'])

        if search:
            schools_fltr = schools.filter(Q(user_id__iexact=user_id) & Q(school_fk__school_name__iexact=search))
        else:
            schools_fltr = schools.filter(Q(user_id__iexact=user_id))

        schools_rtrn = serializers.serialize('json', schools_fltr)

        return HttpResponse(schools_rtrn, content_type="text/json-comment-filtered")

    except Exception as e:
        return HttpResponse('Bad request. The requested "' + str(e) + '" is not valid', status=400)

