import django
from django.db import models

from amoeba.settings import TABLE_PREFIX


class Designations(models.Model):

    designation = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Designations'

    def __str__(self):
        return self.designation
