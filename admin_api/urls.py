from django.urls import path
from admin_api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token,verify_jwt_token
app_name= 'admin_api'

urlpatterns=[
    path('login/',views.login),
]