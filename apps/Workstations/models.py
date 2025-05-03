import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Workstations(BaseModel):
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_workstation")
    work_station = models.CharField(max_length=225)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Workstations'
    
    def __str__(self):
        return self.work_station