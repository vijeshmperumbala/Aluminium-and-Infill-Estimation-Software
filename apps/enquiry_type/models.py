import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class EnquiryTypeModal(BaseModel):

    enquiry_type = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Enquiry_Type'

    def __str__(self):
        return self.enquiry_type
