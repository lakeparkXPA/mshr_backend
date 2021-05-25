from django.urls import path, include
from admin_api.views import account

urlpatterns=[
    path('login/',account.login),
    path('refreshToken/',account.refresh_token)

]