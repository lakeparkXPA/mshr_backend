from django.urls import path, include
from mobile_api.views import student,checkup

urlpatterns=[
    path('addStudent',student.student_add),
    path('editItem',checkup.edit_item),
    path('editItems',checkup.edit_items),
    path('minCheck',student.min_check),
    path('addStudents',student.students_add),
]