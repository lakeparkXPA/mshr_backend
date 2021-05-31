from django.urls import path, include

from admin_api.suburl import dashboard_urls, studentHealth_urls
from admin_api.views import studentHealth_student, dashboard
from admin_api import views

app_name= 'admin_api'

urlpatterns=[

    path('dashboard/',include('admin_api.suburl.dashboard_urls')),
    path('studentHealth/',include('admin_api.suburl.studentHealth_urls')),
    path('account/',include('admin_api.suburl.account_urls')),

]