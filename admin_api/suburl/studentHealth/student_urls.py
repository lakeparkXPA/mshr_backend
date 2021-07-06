from django.urls import path, include
from admin_api.views import studentHealth_student

urlpatterns=[

    path('list', studentHealth_student.student_list),
    path('schoolList', studentHealth_student.school_list),
    path('addStudent', studentHealth_student.student_add),
    path('addStudent/min', studentHealth_student.min_check),
    path('addStudents', studentHealth_student.student_addAll),
    path('modiStudent/<int:student_id>', studentHealth_student.student_get),
    path('modiStudentImg/<int:student_id>', studentHealth_student.student_get_img),
    path('modiStudent', studentHealth_student.student_modify),
    path('delStudent/<int:student_id>', studentHealth_student.student_delete),
    #path('insert/',studentHealth_student.insert),
    path('delStudent',studentHealth_student.student_delete_multi),
    path('listDownload',studentHealth_student.student_listDownload),

]