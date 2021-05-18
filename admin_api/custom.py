from django.core.serializers import json
from rest_framework.response import Response



# def base_exception_handler(exc, context):
#     print("handler")
#     print(context)
#     print(repr(exc))
#     data = {}
#     data['error'] = context
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     #response = exception_handler(exc, context)
#     #
#     # # Now add the HTTP status code to the response.
#     # if response is not None:
#     #     response.data['status_code'] = response.status_code
#
#     return Response("error",status=400)