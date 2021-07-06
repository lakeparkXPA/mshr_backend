from django.urls import path, include



urlpatterns = [
    path('notice/', include('admin_api.suburl.management.notice_urls')),
]