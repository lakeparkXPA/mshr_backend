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


class NoticeFileSerializer(serializers.ModelSerializer):
    """
    공지사항 파일 조회시 사용
    """
    class Meta:
        model = NoticeFile
        fields= ['file_name']



class NoticeListSerializer(serializers.ModelSerializer):
    """
    공지사항 리스트 조회시 사용
    """
    class Meta:
        model = Notice
        fields = ['notice_id','title','create_time']


class NoticeSerializer(serializers.ModelSerializer):
    """
    공지사항 상세 조회시 사용
    """
    class Meta:
        model =Notice
        fields = ['user_name','title','field']



class StudentSerializer(serializers.ModelSerializer):
    """
    학생 리스트 조회시 사용
    """
    class Meta:
        model = Student
        fields = ['school_fk','student_id','student_name','date_of_birth',
                  'gender','grade','grade_class','medical_insurance_number']
    def to_representation(self, instance):
        field_list = ('school_fk','student_id','student_name','date_of_birth',
                  'gender','grade','grade_class','medical_insurance_number')

        data = super().to_representation(instance)
        for field in field_list:
            if data[field] ==None:
                data[field]=''

        return data

class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['school_name','id']