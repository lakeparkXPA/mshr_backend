from django.urls import path, include

from admin_api.suburl import dashboard_urls, studentHealth_urls, account_urls,agency_urls,management_urls
from admin_api.views import studentHealth_student, dashboard
from admin_api import views
from admin_api.views import area
from admin_api.suburl import *
app_name = 'admin_api'

urlpatterns=[

    path('dashboard/',include('admin_api.suburl.dashboard_urls')),
    path('studentHealth/',include('admin_api.suburl.studentHealth_urls')),
    path('account/',include('admin_api.suburl.account_urls')),
    path('agency/', include('admin_api.suburl.agency_urls')),
    path('management/', include('admin_api.suburl.management_urls')),
    path('area', area.area_name, name='area_name'),

]