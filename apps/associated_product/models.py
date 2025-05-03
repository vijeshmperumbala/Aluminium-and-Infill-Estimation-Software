from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class AssociatedProducts(BaseModel):
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_associated_product", null=True, blank=True)
    product_name = models.CharField(max_length=255)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Associated_Products'

    def __str__(self):
        return self.product_name
