from django.urls import path, include
from admin_api.views import dashboard

urlpatterns=[
    path('notice/',dashboard.dashboard_notice_list),
    path('location/',dashboard.dashboard_filter),
    path('notice/<int:notice_id>/', dashboard.dashboard_notice),
    path('notice/<int:notice_id>/<str:file_name>/', dashboard.dashboard_notice_img),

]