from django.contrib.gis.db import models
from enum import Enum

class userlevel(Enum):
    MANAGER = 0
    DOET, HC = 1, 1
    DDOET, DHC = 2, 2
    CC = 3
    SS = 4

class GenderType(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'

