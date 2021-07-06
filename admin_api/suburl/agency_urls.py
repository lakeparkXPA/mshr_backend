from django.urls import path, include



urlpatterns = [
    path('school/', include('admin_api.suburl.agency.school_urls')),
    path('user/', include('admin_api.suburl.agency.user_urls')),
    path('log/', include('admin_api.suburl.agency.log_urls')),
]