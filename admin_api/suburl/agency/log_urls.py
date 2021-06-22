from django.urls import path
from admin_api.views import log

urlpatterns = [
    path('list/', log.log_lst, name='log_lst'),
]