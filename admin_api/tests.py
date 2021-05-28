from django.test import TestCase,Client
import json
from django.db import connection
import unittest
# Create your tests here.



class DashBoardNoticeTest(TestCase):
    def setUp(self):
        """사전 작업 """
        pass

    def tearDown(self):
        """테스트 데이터 삭제"""
        pass


    def test_notice_list_get(self):

        client = Client()

        response = client.get('/admin_api/dashboard/notice/',content_type='application/json')

        self.assertEqual(response.status_code,200)


class DashBoardFilterTest(TestCase):
    def test_dashboard_filter(self):
        client = Client()

        data = {
            'filter' : 'commune',
            'user_id' : 'test1',
            'province' : 'test1',
            'district' : 'test2'

        }


        print(json.dumps(data))
        response = client.post('/admin_api/dashboard/location/',json.dumps(data),content_type='application/x-www-form-urlencoded')
        print(connection.queries)
        self.assertEqual(response.status_code,200)