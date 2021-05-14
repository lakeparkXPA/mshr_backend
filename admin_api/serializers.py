from rest_framework import serializers
from .models import *


class LoginSerializer(serializers.ModelSerializer):

    """Login Serializer"""
    class Meta:
        model = User
        fields = ['user_id','user_level','password']






