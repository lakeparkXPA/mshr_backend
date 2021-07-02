from django.urls import path
from admin_api.views import notice

urlpatterns = [
    path('list', notice.notice_lst, name='user_lst'),
    path('add', notice.notice_add, name='user_add'),
    path('upload/', notice.NoticeFileUpload.as_view()),
    path('detail', notice.notice_detail, name='notice_detail'),
    path('file', notice.notice_file, name='notice_file'),
    path('edit', notice.notice_edit, name='notice_edit'),
    path('remove/<str:pk>', notice.notice_remove, name='notice_remove'),
]
