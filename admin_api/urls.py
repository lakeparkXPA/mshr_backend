from django.urls import path
from admin_api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token,verify_jwt_token
app_name= 'admin_api'

urlpatterns=[
    path('login',views.login),
    path('dashboard/location',views.dashboard_filter),
    path('refreshToken',views.refresh_token),
    path('test',views.test),
    path('dashboard/notice',views.dashboard_notice_list),
    path('dashboard/notice/<int:notice_id>',views.dashboard_notice),
    path('dashboard/notice/<int:notice_id>/<str:file_name>',views.dashboard_notice_img),
    path('studentHealth/student/list',views.studentHealth_student_list),
    path('studentHealth/student/schoolList',views.studentHealth_school_list),
    path('studentHealth/student/addStudent',views.studentHealth_student_add),
    path('studentHealth/student/addStudent/min',views.studentHealth_min_check),
    path('studentHealth/student/addStudents',views.studentHealth_student_addAll),
    path('studentHealth/student/modiStudent/<int:student_id>',views.studentHealth_student_get),
    path('studentHealth/student/modiStudentImg/<int:student_id>',views.studentHealth_student_get_img),
    path('studentHealth/student/modiStudent', views.studentHealth_student_modify),
]