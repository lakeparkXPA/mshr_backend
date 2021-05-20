import simplejwt as simplejwt
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainSerializer


class LoginSerializer(serializers.ModelSerializer):

    """Login Serializer"""

    class Meta:
        model = User
        fields =['user_id', 'user_level', 'password', 'token']


class RefreshTokenSerializer(serializers.ModelSerializer):

    """Refresh Token Serializer"""

    class Meta:
        model = User
        fields = ['token']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    # def to_representation(self, instance):
    #
    #     data = super().to_representation(instance)
    #     if data['user_mobile'] == None:
    #         data['user_mobile'] = ""
    #
    #     return data


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields =  ['district']


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['notice_id','title','create_time']