from django.urls import path, include


app_name= 'mobile_api'

urlpatterns=[


    path('account/',include('mobile_api.suburl.account_urls')),
    path('student/', include('mobile_api.suburl.student_checkup_urls')),

]