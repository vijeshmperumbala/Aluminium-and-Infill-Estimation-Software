from django.db import models
from apps.sealant_types.models import Sealant_Types

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Category(BaseModel):

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_category")
    category = models.CharField(max_length=255, unique=True)
    one_D = models.BooleanField(default=False, null=True, blank=True)
    two_D = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(
        upload_to='category/image', null=True, blank=True)
    is_glass = models.BooleanField(default=False, null=True, blank=True)
    surface_finish = models.BooleanField(default=False, null=True, blank=True)
    sealant = models.BooleanField(default=False, null=True, blank=True)
    points_to_remember = models.BooleanField(
        default=False, null=True, blank=True)
    points = models.CharField(max_length=1000, null=True, blank=True)
    enable_internal_sealant = models.BooleanField(
        default=False)
    enable_external_sealant = models.BooleanField(
        default=False)
    window_or_door_with_divisions = models.BooleanField(default=False)
    
    internal_sealant = models.ForeignKey(
        Sealant_Types, on_delete=models.PROTECT, null=True, blank=False, related_name="category_internal_sealant")
    external_sealant = models.ForeignKey(
        Sealant_Types, on_delete=models.PROTECT, null=True, blank=False, related_name="category_external_sealant")
    invoice_in_quantity = models.BooleanField(
        default=False)
    
    window = models.BooleanField(default=False, null=True, blank=True)
    door = models.BooleanField(default=False, null=True, blank=True)
    is_curtain_wall = models.BooleanField(default=False)
    handrail = models.BooleanField(default=False)
    
    is_ployamide_gasket = models.BooleanField(default=False, null=True, blank=True)
    ployamide_gasket = models.ForeignKey(Sealant_Types, on_delete=models.PROTECT, null=True, blank=False, related_name="category_ployamide_gasket")
    is_transom_gasket = models.BooleanField(default=False, null=True, blank=True)
    transom_gasket = models.ForeignKey(Sealant_Types, on_delete=models.PROTECT, null=True, blank=False, related_name="category_transom_gasket")
    is_mullion_gasket = models.BooleanField(default=False, null=True, blank=True)
    mullion_gasket = models.ForeignKey(Sealant_Types, on_delete=models.PROTECT, null=True, blank=False, related_name="category_mullion_gasket")

    class Meta:
        db_table = f'{TABLE_PREFIX}Categories'

    def __str__(self):
        return self.category
