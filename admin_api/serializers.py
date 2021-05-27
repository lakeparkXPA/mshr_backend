import os

import simplejwt as simplejwt

from rest_framework import serializers
from admin_api.models import *
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




class DistrictSerializer(serializers.ModelSerializer):
    """
     대시보드 필터링에서 사용

     """
    class Meta:
        model = District
        fields =  ['district']


class CommuneSerializer(serializers.ModelSerializer):
    """
    대시보드 필터링에서 사용

    """
    class Meta:
        model = CommuneClinic
        fields = ['commune_clinic']

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


class AddStudentSerializer(serializers.ModelSerializer):
    """학생 등록시 사용"""
    class Meta:
        model = Student
        fields = '__all__'

    def to_representation(self, instance):
        field_list = [field.name for field in Student._meta.get_fields()]
        field_list.remove('checkup')

        data = super().to_representation(instance)
        for field in field_list:
            if data[field] ==None:
                data[field]=''

        return data

    def update(self, instance, validated_data):


        instance.student_name = validated_data.get('student_name',instance.student_name)
        instance.grade = validated_data.get('grade', instance.grade)
        instance.grade_class = validated_data.get('grade_class',instance.grade_class)
        instance.gender = validated_data.get('gender',instance.gender)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.student_number = validated_data.get('student_number', instance.student_number)
        instance.village = validated_data.get('village',instance.village)
        instance.contact = validated_data.get('contact',instance.contact)
        instance.parents_name = validated_data.get('parents_name',instance.parents_name)
        instance.pic = validated_data.get('pic',instance.pic)

        instance.save()
        return instance


class GraduateSerializer(serializers.ModelSerializer):
    """졸업생 등록시 사용"""
    class Meta:
        model = Graduate
        fields = '__all__'



class CheckUpSerializer(serializers.ModelSerializer):
    """체크업 리스트 목록 조회시 사용"""

    class Meta:
        model = Checkup
        fields = '__all__'

    def to_representation(self, instance):
        field_list = [field.name for field in Checkup._meta.get_fields()]
        data = super().to_representation(instance)

        for field in field_list:
            if data[field] == None:
                data[field]=''

        if instance.student_fk:
            student = StudentSerializer(instance.student_fk).data
            data['school_id'] = instance.student_fk.school_fk.school_id
            data['medical_insurance_number'] = student['medical_insurance_number']
            data['student_name'] = student['student_name']
            data['grade'] = student['grade']

        data.pop('graduate_fk')
        data.pop('checked')
        return data
    def update(self, instance, validated_data):
        instance.date = validated_data.get('date',instance.date)
        instance.height = validated_data.get('height',instance.height)
        instance.weight = validated_data.get('weight',instance.weight)
        instance.vision_left = validated_data.get('vision_left',instance.vision_left)
        instance.vision_right = validated_data.get('vision_right',instance.vision_right)
        instance.glasses = validated_data.get('glasses',instance.glasses)
        instance.corrected_left = validated_data.get('corrected_left',instance.corrected_left)
        instance.corrected_right = validated_data.get('corrected_right',instance.corrected_right)
        instance.dental = validated_data.get('dental',instance.dental)
        instance.hearing = validated_data.get('hearing',instance.hearing)
        instance.systolic = validated_data.get('systolic',instance.systolic)
        instance.diastolic = validated_data.get('diastolic',instance.diastolic)
        instance.bust = validated_data.get('bust',instance.bust)

        instance.save()
        return instance


class StudentListSerializer(serializers.ModelSerializer):
    """healthCheckUp/학생 리스트 조회시 사용"""
    class Meta:
        model = Student
        fields = ['student_id','medical_insurance_number','student_name']

class CheckUpGetSerializier(serializers.ModelSerializer):
    """체크업 상세 조회시 사용"""
    class Meta:
        model = Checkup
        fields = '__all__'

    def to_representation(self, instance):
        field_list = [field.name for field in Checkup._meta.get_fields()]
        data = super().to_representation(instance)

        for field in field_list:
            if data[field] == None:
                data[field]=''

        if instance.student_fk:
            student = AddStudentSerializer(instance.student_fk).data

            data['grade'] = student['grade']
            data['grade_class'] = student['grade_class']
            data['student_number'] = student['student_number']
            data['village'] = student['village']
        data.pop('student_fk')
        data.pop('graduate_fk')
        data.pop('checked')
        return data