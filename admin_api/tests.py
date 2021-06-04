from django.test import TestCase,Client
import json
from django.db import connection
import unittest
# Create your tests here.



class DashBoardNoticeTest(unittest.TestCase):
    def setUp(self):
        """사전 작업 """
        print("1")
        pass

    def tearDown(self):
        print("2")
        """테스트 데이터 삭제"""
        pass

    # def test_notice_list_get(self):
    #
    #     client = Client()
    #     print("3")
    #     response = client.get('/admin_api/dashboard/notice/',content_type='application/json')
    #
    #     self.assertEqual(response.status_code,200)
    def test_dashboard_filter(self):
        client = Client()
        print("5")



        response = client.post('/admin_api/studentHealth/student/addStudent/',
                               {"info": {"school_fk" : 3,
                                    "student_name": "test"}})

        print(response.json())
        self.assertEqual(response.status_code,200)

