from django.urls import path, include
from admin_api.views import studentHealth_student

urlpatterns=[

    path('list/', studentHealth_student.studentHealth_student_list),
    path('schoolList/', studentHealth_student.studentHealth_school_list),
    path('addStudent/', studentHealth_student.studentHealth_student_add),
    path('addStudent/min/', studentHealth_student.studentHealth_min_check),
    path('addStudents/', studentHealth_student.studentHealth_student_addAll),
    path('modiStudent/<int:student_id>/', studentHealth_student.studentHealth_student_get),
    path('modiStudentImg/<int:student_id>/', studentHealth_student.studentHealth_student_get_img),
    path('modiStudent/', studentHealth_student.studentHealth_student_modify),
    path('delStudent/<int:student_id>/', studentHealth_student.studentHealth_student_delete),


]