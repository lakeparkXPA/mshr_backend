from admin_api.models import *
from django.db.models import Q, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import permissions, generics
from django.http import FileResponse

from admin_api.package.log import log
from admin_api.permissions import *
from admin_api.serializers import *

from admin_api.serializers import FileUploadSerializer
import requests, shutil, os

# (IsMaster,IsProvince,IsDistrict,)
@api_view(['POST'])
@permission_classes((OverDistrict,))
def notice_lst(request):

    try:
        try:
            user_id = request.data['user_id']
        except:
            raise ValueError(1)

        search = request.data['search']

        user_level = User.objects.get(user_id__exact=user_id).user_level

        if user_level == 0:
            notice_filter = Notice.objects.values('notice_id', 'title', 'create_time', 'user_name')
        elif user_level == 1:
            area = User.objects.select_related('area_fk').get(user_id__exact=user_id).area_fk.province_fk
            area_id = Area.objects.filter(province_fk__exact=area).values('area_id')
            user = User.objects.filter(area_fk__in=area_id).values('user_id')
            notice_filter = Notice.objects.filter(user_fk__exact=user).values('notice_id', 'title',
                                                                              'create_time', 'user_name')
        else:
            raise PermissionError(2)


        if search:
            notice = notice_filter.filter(Q(title__contains=search) |
                                          Q(user_namme__contatins=search)).exclude(notice_id__isnull=True)
        else:
            notice = notice_filter.exclude(notice_id=True)

        #print(notice)
        #print(notice[0])
        notice_data = NoticeGetSerializer(notice,many=True).data



        res = Response(notice_data, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res




#@permission_classes((OverDistrict,))
class NoticeFileUpload(generics.CreateAPIView):
    queryset = NoticeFile.objects.all()
    serializer_class = FileUploadSerializer
    def create(self, request, *args, **kwargs):
        try:
            notice_pk = request.POST.get('notice_fk')
            file_name = request.FILES.get('attachments')
            req_type = request.POST.get('req_type')
            dic = {'file_name': file_name, 'notice_fk': notice_pk}
            file_serializer = FileUploadSerializer(data=dic, partial=True)

            if file_serializer.is_valid():
                if req_type == 'edit':
                    os.remove(str(NoticeFile.objects.get(notice_fk__exact=notice_pk)))
                file_serializer.save()
            else:
                raise ValueError(3)

            res = Response(status=HTTP_200_OK)
            res['HTTP_X_CSTATUS'] = 0
            return res

        except Exception as e:
            res = Response(status=HTTP_400_BAD_REQUEST)
            res['HTTP_X_CSTATUS'] = int(str(e))
            return res


@api_view(['POST'])
@permission_classes((OverProvince,))
def notice_add(request):
    user_id = request.META.get('HTTP_USER_ID', '')
    user_fk = User.objects.filter(user_id__exact=user_id).first()
    user_name = request.data['publisher']
    title = request.data['title']
    contents = request.data['contents']

    notice = Notice()
    notice.title = title
    notice.user_name = user_name
    notice.user_fk = user_fk
    notice.field = contents

    notice.save()

    if request.FILES.getlist('attachments'):
        notice_return = {'notice_fk': notice.notice_id, 'req_type': 'add'}
        notice_data = {'attachments': request.FILES.get('attachments')}

        response = requests.post('http://127.0.0.1:8000/admin_api/management/notice/upload/',
                                 files=notice_data, data=notice_return)
        try:
            res = Response(status=HTTP_200_OK)
            res['HTTP_X_CSTATUS'] = response.headers['HTTP_X_CSTATUS']
            return res
        except:
            pass
    log(request, typ='Add Notice', content='Insert Notice ' + user_id)

    res = Response(status=HTTP_200_OK)
    res['HTTP_X_CSTATUS'] = 0
    return res



@api_view(['GET'])
@permission_classes((OverDistrict,))
def notice_detail(request):
    try:
        notice_id = request.GET.get('notice_id')

        if not notice_id:
            ValueError(4)

        notice_select = Notice.objects.prefetch_related('noticefile_set').filter(notice_id__exact=notice_id).\
            extra(select={'file_name': "coalesce(file_name, '')"}).values(
            'user_name', 'title', 'field', file_name=F('noticefile__file_name'))

        res = Response(notice_select, status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['GET'])
@permission_classes((OverDistrict,))
def notice_file(request):
    try:
        notice_id = request.GET.get('notice_id')
        if not notice_id:
            ValueError(4)

        file = NoticeFile.objects.get(notice_fk__exact=notice_id).file_name

        if not file:
            raise ValueError(3)

        return FileResponse(file, as_attachment=True)

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['PUT'])
@permission_classes((OverDistrict,))
def notice_edit(request):
    try:
        user_id = request.META.get('HTTP_USER_ID', '')
        user_fk = User.objects.filter(user_id__exact=user_id).first()
        user_name = request.data['publisher']
        title = request.data['title']
        contents = request.data['contents']
        notice_id = request.data['notice_id']

        try:
            notice = Notice.objects.get(notice_id__exact=notice_id)

            notice.title = title
            notice.user_name = user_name
            notice.user_fk = user_fk
            notice.field = contents

            notice.save()
        except:
            ValueError(4)

        if request.FILES.getlist('attachments'):
            notice_return = {'notice_fk': notice.notice_id, 'req_type': 'edit'}
            notice_data = {'attachments': request.FILES.get('attachments')}

            file_old_pk = NoticeFile.objects.get(notice_fk__exact=notice.notice_id).id

            requests.post('http://127.0.0.1:8000/admin_api/management/notice/upload/',
                          files=notice_data, data=notice_return)

            NoticeFile.objects.get(id=file_old_pk).delete()

        # TODO---- Enable block later
        # log(request, typ='Add school', content='Insert school ' + school_id)

        res = Response(status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res


@api_view(['DELETE', 'GET'])
@permission_classes((OverDistrict,))
def notice_remove(request, pk):
    try:
        try:
            file = NoticeFile.objects.get(notice_fk__exact=pk).file_name
            if file:
                shutil.rmtree(MEDIA_ROOT + '/notice/' + str(pk))

            notice_file_del = NoticeFile.objects.get(notice_fk__exact=pk)
            notice_file_del.delete()
        except:
            pass
        try:
            notice_del = Notice.objects.get(notice_id__exact=pk)
            notice_del.delete()
        except:
            ValueError(4)

        # TODO---- Enable block later
        # log(request, typ='Delete school', content='Delete school ' + str(pk))
        res = Response(status=HTTP_200_OK)
        res['HTTP_X_CSTATUS'] = 0
        return res

    except Exception as e:
        res = Response(status=HTTP_400_BAD_REQUEST)
        res['HTTP_X_CSTATUS'] = int(str(e))
        return res

