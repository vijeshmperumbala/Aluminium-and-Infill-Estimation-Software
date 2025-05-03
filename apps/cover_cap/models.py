import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class CoverCap_PressurePlates(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_covercap")
    
    cap_name = models.CharField(max_length=225)
    cap_code = models.CharField(max_length=50)
    cap_thickness = models.DecimalField(max_digits=5, decimal_places=2)
    cap_weight_lm = models.DecimalField(max_digits=5, decimal_places=2)
    cap_formula = models.CharField(max_length=50)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}CoverCap_and_PressurePlates'

    def __str__(self):
        return self.cap_name
