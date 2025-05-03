from django.db import models

from apps.designations.models import Designations
from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Signatures(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_signature")
    signature = models.CharField(max_length=255, null=True, blank=True)
    designation = models.ForeignKey(Designations, on_delete=models.PROTECT, related_name="signature_designation")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="signature_user")
    image = models.ImageField(upload_to='signatures/image', null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Signature'

    def __str__(self):
        return self.signature
