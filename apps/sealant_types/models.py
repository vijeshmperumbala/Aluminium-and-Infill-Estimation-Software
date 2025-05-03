import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Sealant_Types(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_sealant_types")
    sealant_type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Sealant_Types'

    def __str__(self):
        return self.sealant_type
