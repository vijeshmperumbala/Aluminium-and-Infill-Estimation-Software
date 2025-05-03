import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Surface_finish(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_surface_finish")
    surface_finish = models.CharField(max_length=255, null=True, blank=True)
    # surface_finish_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Surface_finish'

    def __str__(self):
        return self.surface_finish


class SurfaceFinishColors(models.Model):
    surface_finish = models.ForeignKey(Surface_finish, on_delete=models.PROTECT, null=True, blank=True, related_name="color_surface_finish")
    color = models.CharField(max_length=225)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SurfaceFinishColors'

    def __str__(self):
        return self.color