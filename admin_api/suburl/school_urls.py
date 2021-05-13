from django.urls import path, include
import admin_api.views

urlpatterns = [
    path('list/', admin_api.views.school_lst, name='school_lst')

]