from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class RatingHead(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_rating_head", null=True, blank=True)
    head = models.CharField(max_length=255)

    class Meta:
        db_table = f'{TABLE_PREFIX}RatingHead'

    def __str__(self):
        return self.head

