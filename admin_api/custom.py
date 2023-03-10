from django.core.serializers import json

from django.core.exceptions import PermissionDenied
from django.db import connections, models
from django.http import Http404


from rest_framework import exceptions
from rest_framework.response import Response


from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response




