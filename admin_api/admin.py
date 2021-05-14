from django.contrib import admin
from admin_api.models import *
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.get_fields()]



@admin.register(Checkup)
class CheckupAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Checkup._meta.get_fields()]


@admin.register(CommuneClinic)
class CommuneClinicAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommuneClinic._meta.get_fields()]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = [field.name for field in District._meta.get_fields()]

@admin.register(Graduate)
class GraduateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Graduate._meta.get_fields()]

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Log._meta.get_fields()]

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notice._meta.get_fields()]

@admin.register(NoticeFile)
class NoticeFileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NoticeFile._meta.get_fields()]

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Province._meta.get_fields()]

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = [field.name for field in School._meta.get_fields()]

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Area._meta.get_fields()]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Student._meta.get_fields()]