import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Vehicles(models.Model):

    vehicle_name = models.CharField(max_length=225)

    class Meta:
        db_table = f'{TABLE_PREFIX}Vehicles'

    def __str__(self):
        return self.vehicle_name


class Drivers(models.Model):

    driver = models.CharField(max_length=225)

    class Meta:
        db_table = f'{TABLE_PREFIX}Drivers'

    def __str__(self):
        return self.driver
