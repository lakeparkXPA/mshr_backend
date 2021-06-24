from django.urls import path
from admin_api.views import user

urlpatterns = [
    path('list', user.user_lst, name='user_lst'),
    path('check', user.user_check, name='user_check'),
    path('add', user.user_add, name='user_add'),
    path('reset', user.reset_pw, name='reset_pw'),
    path('detail', user.user_detail, name='user_detail'),
    path('edit', user.user_edit, name='user_edit'),
    path('remove/<str:pk>', user.user_remove, name='user_remove'),
]
