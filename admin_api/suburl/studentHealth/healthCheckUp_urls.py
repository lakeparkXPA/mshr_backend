from django.urls import path, include
from admin_api.views import studentHealth_healthCheckUp


urlpatterns=[
    path('getCheckUpList/',studentHealth_healthCheckUp.list),
    path('getStudentList/',studentHealth_healthCheckUp.stuList),
    path('addCheckUp/',studentHealth_healthCheckUp.addCheckUp),
    path('modiCheckUp/',studentHealth_healthCheckUp.modiCheckUp),

    path('getCheckUp/',studentHealth_healthCheckUp.getCheckUp),
    path('delCheckUp/<int:checkup_id>',studentHealth_healthCheckUp.delCheckUp),
    path('delCheckUp/',studentHealth_healthCheckUp.delChekUpMulti),
    ]