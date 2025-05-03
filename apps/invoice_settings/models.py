import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Invoice_Settings(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_invoice_settings")
    invoice_stage = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Invoice_Settings'

    def __str__(self):
        return self.invoice_stage
