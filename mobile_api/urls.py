from django.urls import path, include


app_name= 'mobile_api'

urlpatterns=[

    path('dashboard/',include('admin_api.suburl.dashboard_urls')),
    path('studentHealth/',include('admin_api.suburl.studentHealth_urls')),
    path('account/',include('mobile_api.suburl.account_urls')),
    path('student/', include('mobile_api.suburl.student_checkup_urls')),

]