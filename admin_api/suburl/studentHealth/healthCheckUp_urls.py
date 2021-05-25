from django.urls import path, include
from admin_api.views import studentHealth_healthCheckUp


urlpatterns=[
    path('getCheckUpList/',studentHealth_healthCheckUp.studentHealth_healthCheckUp_list),
    path('getStudentList/',studentHealth_healthCheckUp.studentHealth_healthCheckUp_stuList),
]