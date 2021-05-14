
from django.shortcuts import render
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.status import *
from rest_framework.views import *
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
# Create your views here.
from admin_api.models import *
from admin_api.permissions import *
from admin_api.serializers import *
import hashlib, jwt
from django.contrib.auth import authenticate
import datetime
from rest_framework_jwt.views import obtain_jwt_token


from mshr_backend.settings import ALGORITHM, SECRET_KEY
@api_view(['POST'])
@permission_classes([AllowAny]) #모든 사람에게 권한 허용
def login(request):
    """ login api"""

    try:

        obj = User.objects.get(user_id=request.data['user_id'])
        user = LoginSerializer(obj).data

        if hashlib.sha256(request.data['password'].encode()).hexdigest() == user['password']:

            payload = {}
            if user['user_level'] == 0:
                payload['user_level'] = 'master'

            elif user['user_level'] ==1:
                payload['user_level'] ='province'

            elif user['user_level']==2:
                payload['user_level'] ='district'

            elif user['user_level']==3:
                payload['user_level'] ='commune'

            elif user['user_lvel']==4 :
                payload['user_level'] ='school'

            payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(days=30)
            token = jwt.encode(payload,SECRET_KEY,ALGORITHM)
            data = {}
            data['token'] = token
            return Response(data)

        else:
            return Response("password incorrupt",status=HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response('Error : ' + str(e),status=HTTP_400_BAD_REQUEST)





