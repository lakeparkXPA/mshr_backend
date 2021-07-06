from django.urls import path
from admin_api.views import school

urlpatterns = [
    path('list', school.school_lst, name='school_lst'),
    path('check', school.school_check, name='school_check'),
    path('add', school.school_add, name='school_add'),
    path('detail', school.school_detail, name='school_detail'),
    path('edit', school.school_edit, name='school_edit'),
    path('remove/<str:pk>', school.school_remove, name='school_remove'),
]
