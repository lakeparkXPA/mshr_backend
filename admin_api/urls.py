from django.urls import path
from admin_api import views,dashboardView,studentHealthStudentView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token,verify_jwt_token
app_name= 'admin_api'

urlpatterns=[
    path('login',views.login),
    path('dashboard/location',dashboardView.dashboard_filter),
    path('refreshToken',views.refresh_token),

    path('dashboard/notice',dashboardView.dashboard_notice_list),
    path('dashboard/notice/<int:notice_id>',dashboardView.dashboard_notice),
    path('dashboard/notice/<int:notice_id>/<str:file_name>',dashboardView.dashboard_notice_img),
    path('studentHealth/student/list',studentHealthStudentView.studentHealth_student_list),
    path('studentHealth/student/schoolList',studentHealthStudentView.studentHealth_school_list),
    path('studentHealth/student/addStudent',studentHealthStudentView.studentHealth_student_add),
    path('studentHealth/student/addStudent/min',studentHealthStudentView.studentHealth_min_check),
    path('studentHealth/student/addStudents',studentHealthStudentView.studentHealth_student_addAll),
    path('studentHealth/student/modiStudent/<int:student_id>',studentHealthStudentView.studentHealth_student_get),
    path('studentHealth/student/modiStudentImg/<int:student_id>',studentHealthStudentView.studentHealth_student_get_img),
    path('studentHealth/student/modiStudent', studentHealthStudentView.studentHealth_student_modify),
    path('studentHealth/student/delStudent/<int:student_id>', studentHealthStudentView.studentHealth_student_delete),

]