from django.db import models

# Create your models here.
from django.db import models
class Area(models.Model):
    area_id = models.AutoField(primary_key=True)
    province_fk = models.ForeignKey('Province', models.DO_NOTHING, db_column='province_fk', blank=True, null=True)
    district_fk = models.ForeignKey('District', models.DO_NOTHING, db_column='district_fk', blank=True, null=True)
    commune_clinic_fk = models.ForeignKey('CommuneClinic', models.DO_NOTHING, db_column='commune_clinic_fk', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'area'


class Checkup(models.Model):
    student_fk = models.ForeignKey('Student', models.DO_NOTHING, db_column='student_fk', blank=True, null=True)
    graduate_fk = models.ForeignKey('Graduate', models.DO_NOTHING, db_column='graduate_fk', blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    vision_left = models.FloatField(blank=True, null=True)
    vision_right = models.FloatField(blank=True, null=True)
    glasses = models.IntegerField(blank=True, null=True)
    corrected_left = models.FloatField(blank=True, null=True)
    corrected_right = models.FloatField(blank=True, null=True)
    dental = models.IntegerField(blank=True, null=True)
    hearing = models.IntegerField(blank=True, null=True)
    systolic = models.FloatField(blank=True, null=True)
    diastolic = models.FloatField(blank=True, null=True)
    bust = models.FloatField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'checkup'


class CommuneClinic(models.Model):
    commune_clinic_id = models.AutoField(primary_key=True)
    district_fk = models.ForeignKey('District', models.DO_NOTHING, db_column='district_fk', blank=True, null=True)
    commune_clinic = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'commune_clinic'


class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    province_fk = models.ForeignKey('Province', models.DO_NOTHING, db_column='province_fk', blank=True, null=True)
    district = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'district'


class Graduate(models.Model):
    graduate_id = models.AutoField(primary_key=True)
    school_fk = models.ForeignKey('School', models.DO_NOTHING, db_column='school_fk')
    student_name = models.CharField(max_length=30)
    grade = models.IntegerField()
    grade_class = models.CharField(max_length=10)
    gender = models.CharField(max_length=5)
    date_of_birth = models.DateField()
    student_number = models.CharField(max_length=30, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=30, blank=True, null=True)
    parents_name = models.CharField(max_length=30, blank=True, null=True)
    medical_insurance_number = models.CharField(max_length=30, blank=True, null=True)
    pic = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'graduate'


class Log(models.Model):
    user_fk = models.ForeignKey('User', models.DO_NOTHING, db_column='user_fk', blank=True, null=True)
    user_id = models.CharField(max_length=50)
    log_time = models.DateTimeField(blank=True, null=True)
    log_type = models.CharField(max_length=255, blank=True, null=True)
    log_content = models.CharField(max_length=100, blank=True, null=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    user_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'log'


class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    user_fk = models.ForeignKey('User', models.DO_NOTHING, db_column='user_fk', blank=True, null=True)
    user_name = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255)
    field = models.TextField()
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notice'


class NoticeFile(models.Model):
    notice_fk = models.ForeignKey(Notice, models.DO_NOTHING, db_column='notice_fk')
    file_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'notice_file'


class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    province = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'province'


class School(models.Model):
    area_fk = models.ForeignKey(Area, models.DO_NOTHING, db_column='area_fk', blank=True, null=True)
    school_id = models.CharField(max_length=100)
    school_name = models.CharField(max_length=50)
    agency_category = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    director = models.CharField(max_length=30, blank=True, null=True)
    email_address = models.CharField(max_length=50, blank=True, null=True)
    commune_center_tel = models.CharField(max_length=30, blank=True, null=True)
    department_head_tel = models.CharField(max_length=30, blank=True, null=True)
    staff_tel = models.CharField(max_length=30)
    remarks = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'school'


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    school_fk = models.ForeignKey(School, models.DO_NOTHING, db_column='school_fk')
    student_name = models.CharField(max_length=30)
    grade = models.IntegerField()
    grade_class = models.CharField(max_length=10)
    gender = models.CharField(max_length=5)
    date_of_birth = models.DateField()
    student_number = models.CharField(max_length=30, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=30, blank=True, null=True)
    parents_name = models.CharField(max_length=30, blank=True, null=True)
    medical_insurance_number = models.CharField(max_length=30, blank=True, null=True)
    pic = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student'


class User(models.Model):
    school_fk = models.ForeignKey(School, models.DO_NOTHING, db_column='school_fk', blank=True, null=True)
    area_fk = models.ForeignKey(Area, models.DO_NOTHING, db_column='area_fk', blank=True, null=True)
    user_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    email_address = models.CharField(max_length=50, blank=True, null=True)
    user_group = models.CharField(max_length=50)
    user_level = models.IntegerField()
    user_tel = models.CharField(max_length=30)
    user_mobile = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=255)
    token = models.CharField(max_length=255,blank=True,null=True)

    class Meta:
        managed = False
        db_table = 'user'
