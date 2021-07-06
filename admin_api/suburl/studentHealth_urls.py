from django.urls import path, include


urlpatterns=[
    path('student/',include('admin_api.suburl.studentHealth.student_urls')),
    path('healthCheckUp/',include('admin_api.suburl.studentHealth.healthCheckUp_urls')),
]