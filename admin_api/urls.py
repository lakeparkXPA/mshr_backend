from django.urls import path
from admin_api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token,verify_jwt_token
app_name= 'admin_api'

urlpatterns=[
    path('login',views.login),
    path('dashboard/location',views.dashboard_filter),
    path('refreshToken',views.refresh_token),
    path('test',views.test),
    path('dashboard/notice',views.dashboard_notice_list),
    path('dashboard/notice/<int:notice_id>',views.dashboard_notice),
]