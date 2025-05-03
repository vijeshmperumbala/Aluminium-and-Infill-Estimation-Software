import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Tags(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_tag")
    tag_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    tag_color = models.CharField(max_length=10 ,null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Tags'

    def __str__(self):
        return self.tag_name
