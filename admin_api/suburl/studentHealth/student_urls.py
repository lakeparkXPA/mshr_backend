from django.urls import path, include
from admin_api.views import studenthealth_student

urlpatterns=[

    path('list/', studenthealth_student.studentHealth_student_list),
    path('schoolList/', studenthealth_student.studentHealth_school_list),
    path('addStudent/', studenthealth_student.studentHealth_student_add),
    path('addStudent/min/', studenthealth_student.studentHealth_min_check),
    path('addStudents/', studenthealth_student.studentHealth_student_addAll),
    path('modiStudent/<int:student_id>/', studenthealth_student.studentHealth_student_get),
    path('modiStudentImg/<int:student_id>/',studenthealth_student.studentHealth_student_get_img),
    path('modiStudent/', studenthealth_student.studentHealth_student_modify),
    path('delStudent/<int:student_id>/', studenthealth_student.studentHealth_student_delete),


]