from rest_framework.test import APIClient, force_authenticate
from admin_api.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from admin_api.views.notice import notice_add
import json
"""
factory = APIClient()
url = 'http://3.34.199.113:8000/agency/user/'
print('user')
url_pls = 'list/'
dic = {"user_id": "test1", "search": ""}
request = factory.post(url + url_pls, dic, format='json')
print(url_pls)
print(request.content)
url_pls = 'check?user_id=junha'
request = factory.get(url + url_pls)
print(url_pls)
print(request.content)
url_pls = 'add/'  # checked?
dic = {"province": "test1",
       "district": "",
       "commune_clinic": "",
       "school_name": "",
       "user_group": "DoH",
       "user_id": "junha",
       "user_name": "junha",
       "user_tel": "01012345678",
       "email_address": "",
       "user_mobile": ""
       }
request = factory.post(url + url_pls, dic, format='json')
print(url_pls)
print(request.content)
url_pls = 'reset?user_id=junha'
request = factory.get(url + url_pls)
print(url_pls)
print(request.content)
url_pls = 'detail?user_id=junha'
request = factory.get(url + url_pls)
print(url_pls)
print(request.content)
url_pls = 'edit/'
dic = {"province": "test1",
       "district": "",
       "commune_clinic": "",
       "school_name": "",
       "user_group": "DoH",
       "user_id": "junha",
       "user_name": "junha",
       "user_tel": "01012345679",
       "email_address": "",
       "user_mobile": ""
       }
request = factory.put(url + url_pls, dic, format='json')
print(url_pls)
print(request.content)
url_pls = 'remove/junha'
request = factory.delete(url + url_pls)
print(url_pls)
print(request.content)
"""

# factory = APIClient()
#
# url = 'http://3.34.199.113:8000/admin_api/agency/log/'
#
# print('user')
#
# url_pls = 'list/'
# dic = {"user_id": "test1", "search": ""}
# request = factory.post(url + url_pls, dic, format='json')
# print(url_pls)
# print(request.content)

#
# factory = APIClient()
# data = File(open('media/notice/6/printMgmt_1.pdf', 'rb'))
# upload_file = SimpleUploadedFile('test.pdf',data.read(), content_type='multipart/form-data')
#
# url = 'http://3.34.199.113:8000/admin_api/management/notice/'
#
# print('notice')
#
# url_pls = 'add/'
# dic = {"attachments": upload_file, "publisher": "test1", "title": "test", "contents": "test"}
# request = factory.post(url + url_pls, dic, HTTP_USER_ID='test1', format="multipart",)
# print(url_pls)
# print(request.content)

factory = APIClient()

data = File(open('../media/notice/44/test-1625040706118.json', 'rb'))
upload_file = SimpleUploadedFile('test-12345.json', data.read(), content_type='multipart/form-data')

url = 'https://api.vnschoolhealth.net/admin_api/management/notice/'

print('add')
auth = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoIjoiYWNjZXNzIiwiZXhwIjoxNjI2NzU4OTcxfQ.WEHWZNBaFtDGQUQ-UBmoRp711Luw2uJFo8GasCs44OU'
factory.credentials(HTTP_AUTHORIZATION='Token ' + auth)
url_pls = 'add'
dic = {"attachments": upload_file,"publisher": "manager", "title": "4", "contents": "test"}
request = factory.post(url + url_pls, dic, HTTP_USER_ID='manager', format="multipart",)

print(url_pls)
print(request.content)

import requests
# notice_return = {
#     "nameVal": "junha",
#     "idVal": "hjshljy1@docl.org",
#     "pwVal": "docl2020!!",
#     "titleVal": "test",
#     "groupVal": "group",
#     "phoneVal": "01071246173"
# }
#
# response = requests.post('https://testgroup.docl.org/api/register.php', data=notice_return)
# print(response.content)


#
# factory = APIClient()
#
# url = 'http://3.34.199.113:8000/admin_api/management/notice/'
#
# print('notice')
#
# url_pls = 'file?notice_id=16'
# request = factory.get(url + url_pls, HTTP_USER_ID='test1', format="json",)
# print(url_pls)
# print(request.content)

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mshr_backend.settings")
import django
django.setup()