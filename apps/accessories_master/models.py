import django
from django.db import models

from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from apps.UoM.models import UoM
from apps.brands.models import AccessoriesBrands, Countries
from amoeba.settings import TABLE_PREFIX

STATUS = [
    (1, 'Published'),
    (2, 'Draft'),
    (3, 'Scheduled'),
    (4, 'Inactive')
]


class Accessories(BaseModel):

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_accessory", null=True, blank=True)
    accessory_name = models.CharField(max_length=255)
    accessory_category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="accessory_cat", null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.CASCADE,
                            related_name="accessory_uom")
    description = models.CharField(max_length=255, null=True, blank=True)
    effective_from = models.DateTimeField(default=django.utils.timezone.now)
    country = models.ForeignKey(Countries, on_delete=models.PROTECT,
                                related_name="accessory_country", null=True, blank=True)
    accessory_brand = models.ForeignKey(
        AccessoriesBrands, on_delete=models.PROTECT, related_name="accessory_brand", null=True, blank=True)
    image = models.ImageField(upload_to='accessories/image', blank=True)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Accessories'

    def __str__(self):
        return self.accessory_name
