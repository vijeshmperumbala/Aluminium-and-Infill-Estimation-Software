import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Provisions(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_provisions")
    provisions = models.CharField(max_length=255, null=True, blank=True)
    provisions_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Provisions'

    def __str__(self):
        return self.provisions
