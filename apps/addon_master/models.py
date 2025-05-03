from django.db import models

from apps.user.models import BaseModel, User

from amoeba.settings import TABLE_PREFIX


class Addons(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_addon")
    addon = models.CharField(max_length=255, unique=True)
    linear_meter = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, null=True, blank=True)
    sqm = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    unit = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Addons'

    def __str__(self):
        return self.addon
