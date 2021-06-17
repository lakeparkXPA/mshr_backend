import datetime
import os

import simplejwt as simplejwt

from rest_framework import serializers
from mobile_api.models import *


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

class AddStudentSerializer(serializers.ModelSerializer):
    """학생 등록시 사용"""
    class Meta:
        model = Student
        fields = '__all__'

    # def to_representation(self, instance):
    #     field_list = [field.name for field in Student._meta.get_fields()]
    #     field_list.remove('checkup')
    #
    #     data = super().to_representation(instance)
    #     for field in field_list:
    #         if data[field] ==None:
    #             data[field]=''
    #
    #     return data

    # def update(self, instance, validated_data):
    #
    #
    #     instance.student_name = validated_data.get('student_name',instance.student_name)
    #     instance.grade = validated_data.get('grade', instance.grade)
    #     instance.grade_class = validated_data.get('grade_class',instance.grade_class)
    #     instance.gender = validated_data.get('gender',instance.gender)
    #     instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
    #     instance.student_number = validated_data.get('student_number', instance.student_number)
    #     instance.village = validated_data.get('village',instance.village)
    #     instance.contact = validated_data.get('contact',instance.contact)
    #     instance.parents_name = validated_data.get('parents_name',instance.parents_name)
    #
    #     instance.save()
    #     return instance

class AddCheckUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkup
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.height = validated_data.get('height',instance.height)
        instance.weight = validated_data.get('weight',instance.weight)
        instance.vision_right = validated_data.get('vision_right',instance.vision_right)
        instance.vision_left = validated_data.get('vision_left', instance.vision_left)
        instance.glasses = validated_data.get('glasses',instance.glasses)
        instance.corrected_left = validated_data.get('corrected_left', instance.corrected_left)
        instance.corrected_right = validated_data.get('corrected_right', instance.corrected_right)
        instance.dental = validated_data.get('dental',instance.dental)
        instance.hearing = validated_data.get('hearing', instance.hearing)
        instance.systolic = validated_data.get('systolic', instance.systolic)
        instance.diastolic = validated_data.get('diastolic', instance.diastolic)
        instance.bust = validated_data.get('bust', instance.bust)
        instance.checked = 1
        instance.save()

        return instance