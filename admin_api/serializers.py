import datetime
import os

import simplejwt as simplejwt

from rest_framework import serializers
from admin_api.models import *
from rest_framework_simplejwt.serializers import TokenObtainSerializer


class LoginSerializer(serializers.ModelSerializer):

    """Login Serializer"""

    class Meta:
        model = User
        fields =['user_id', 'user_level', 'password', 'token','area_fk','school_fk']


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
        fields = ['district']


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
                  'gender','grade','grade_class','medical_insurance_number','village']

    def to_representation(self, instance):
        field_list = ('student_id')

        data = super().to_representation(instance)
        for key in data.keys():
            if not data[key]:
                if key in field_list:
                    data[key] = -1
                else:
                    data[key] = ''

        return data


class StudentDownloadSerializer(serializers.ModelSerializer):
    """
    학생 리스트 조회시 사용
    """
    class Meta:
        model = Student
        fields = ['student_id','student_name','grade','grade_class','student_number','date_of_birth',
                  'gender','medical_insurance_number','village','contact','parents_name']

    def to_representation(self, instance):

        # school = SchoolSerializer(instance.student_fk).data
        # print(school)
        data = {}
        school = SchoolSerializer(instance.school_fk).data
        data['school_id'] = school['school_id']

        data_instance = super().to_representation(instance)

        field_list = ['student_id', 'student_name', 'grade',
                      'grade_class', 'student_number', 'date_of_birth','gender',
                      'medical_insurance_number', 'village', 'contact', 'parents_name']
        for field in field_list:
            if data_instance[field] ==None:
                data_instance[field]=''

        data.update(data_instance)
        return data

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['school_id']

class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['school_name','id']

class SchoolDownLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        #fields = ['school_name,school_id']
        fields = '__all__'

class AddStudentSerializer(serializers.ModelSerializer):
    """학생 등록시 사용"""
    class Meta:
        model = Student
        fields = '__all__'

    def to_representation(self, instance):
        field_list = [field.name for field in Student._meta.get_fields()]
        field_list.remove('checkup')

        data = super().to_representation(instance)
        for key in data.keys():
            if not data[key]:
                data[key] = ''

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
            if not data[field]:
                data[field] = ''

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

class CheckUpListSerializer(serializers.ModelSerializer):
    """체크업 리스트 목록 조회시 사용"""

    class Meta:
        model = Checkup
        fields = '__all__'

    def to_representation(self, instance):
        field_list = ['vision_left', 'vision_right', 'corrected_left', 'corrected_right', 'dental', 'hearing',
                      'systolic', 'diastolic', 'bust', 'glasses', 'weight', 'height', 'student_fk']
        data = super().to_representation(instance)

        for key in data.keys():
            if not data[key]:
                if key in field_list:
                    data[key] = -1
                else:
                    data[key] = ''

        if instance.student_fk:
            student = StudentSerializer(instance.student_fk).data

        data['school_id'] = instance.student_fk.school_fk.school_id if instance.student_fk else ''
        data['medical_insurance_number'] = student['medical_insurance_number'] if instance.student_fk else ''
        data['student_name'] = student['student_name'] if instance.student_fk else ''
        data['grade'] = student['grade'] if instance.student_fk else -1
        data['dob'] = student['date_of_birth'] if instance.student_fk else ''
        data['grade_class'] = student['grade_class'] if instance.student_fk else ''
        data['gender'] = student['gender'] if instance.student_fk else ''
        birth_year = datetime.datetime.strptime(student['date_of_birth'], "%Y-%m-%d").year if instance.student_fk else -1
        cur_year = datetime.datetime.today().year
        data['age'] = cur_year - birth_year + 1 if instance.student_fk else -1
        data['village'] = student['village'] if instance.student_fk else ''
        data['hc_year'] = str(datetime.datetime.strptime(data['date'], "%Y-%m-%d").year)


        if data['height'] == -1 or data['weight'] == -1:
            data['bmi'] = 0
        else:
            height_m = data['height'] / 100
            data['bmi'] = round(data['weight'] / (height_m ** 2), 2)

        data.pop('graduate_fk')
        data.pop('checked')
        return data


class CheckUpDownSerializer(serializers.ModelSerializer):
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

        total_data = {}
        return_data = {}
        if instance.student_fk:
            student = StudentDownloadSerializer(instance.student_fk).data
            school = SchoolDownLoadSerializer(instance.student_fk.school_fk).data

            total_data['school_id'] = school['school_id']
            total_data['school_name'] = school['school_name']
            total_data['student_name'] = student['student_name']
            total_data['grade'] = student['grade']
            total_data['grade_class'] = student['grade_class']
            total_data['student_number'] = student['student_number']
            total_data['medical_insurance_number'] = student['medical_insurance_number']
            total_data['date_of_birth'] =student['date_of_birth']
            birth_year =datetime.datetime.strptime(total_data['date_of_birth'],"%Y-%m-%d").year
            cur_year = datetime.datetime.today().year
            total_data['age'] = cur_year-birth_year+1
            total_data['gender'] = student['gender']
            total_data.update(data)

            if total_data['height'] == '' or total_data['weight'] == '':
                total_data['bmi'] = 0
            else:
                height_m = total_data['height']/100
                total_data['bmi'] = round(total_data['weight'] / (height_m**2),2)

            total_data.pop('graduate_fk')
            total_data.pop('checked')
            total_data.pop('id')
            total_data.pop('student_fk')

            return_data['date'] = total_data['date']

            total_data.pop('date')
            return_data.update(total_data)
        return return_data



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

        for key in data.keys():
            if not data[key]:
                data[key] = ''

        if instance.student_fk:
            student = AddStudentSerializer(instance.student_fk).data
            school_name = School.objects.get(id=student['school_fk']).school_name
            print(school_name)
            print(data['height'])
            print(type(data['height']))
            data['grade'] = student['grade']
            data['grade_class'] = student['grade_class']
            data['student_number'] = student['student_number']
            data['village'] = student['village']
            data['medical_insurance_number'] = student['medical_insurance_number']
            data['date_of_birth'] = student['date_of_birth']
            data['gender'] = student['gender']
            data['school_fk'] = student['school_fk']
            data['student_id'] = student['student_id']
            data['student_name'] = student['student_name']
            data['school_name'] = school_name


            if not data['height'] or not data['weight']:
                data['bmi'] = 0
            else:
                height_m = data['height'] / 100
                data['bmi'] = round(data['weight'] / (height_m ** 2), 2)
        data.pop('student_fk')
        data.pop('graduate_fk')
        data.pop('checked')
        return data


class AddStudentsSerializer(serializers.ModelSerializer):
    """학생 등록시 사용"""
    class Meta:
        model = Student
        fields = '__all__'


class FileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoticeFile
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.notice_fk = validated_data.get('notice_fk', instance.notice_fk)
        instance.file_name = validated_data.get('file_name', instance.file_name)

        instance.save()

        return instance


class NoticeGetSerializer(serializers.ModelSerializer):
    """notice list 조회시 사용"""
    class Meta:
        model = Notice
        fields = ['notice_id','title','create_time','user_name']

    def to_representation(self, instance):
        field_list = ['notice_id', 'title', 'create_time', 'user_name']

        data = super().to_representation(instance)

        for field in field_list:
            if field == 'create_time':
                if data[field] !=None:
                    timeList = data[field].split("T")
                    data[field] = timeList[0] + ' '+ timeList[1]
                    data[field] = data[field][0:19]
                else:
                    data[field]=''
            elif data[field] == None:
                data[field]=''



        return data


