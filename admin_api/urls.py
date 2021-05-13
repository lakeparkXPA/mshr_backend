from django.urls import path, include

urlpatterns = [
    path('school/', include('admin_api.suburl.school_urls'))

]