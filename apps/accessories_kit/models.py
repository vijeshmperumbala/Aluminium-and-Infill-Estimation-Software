from django.db import models

from apps.user.models import BaseModel, User
from apps.accessories_master.models import Accessories
from apps.product_master.models import Product, Product_Accessories

from amoeba.settings import TABLE_PREFIX


class AccessoriesKit(BaseModel):

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_acc_kit", null=True, blank=True)
    kit_name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True,
                                blank=True, related_name="accessory_kit_product")
    description = models.CharField(max_length=255, null=True, blank=True)
    kit_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=00.00)
    
    accessory_product = models.ForeignKey(Product_Accessories, on_delete=models.PROTECT, null=True,
                                  blank=True, related_name="kit_item_accessorysin_kit")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}AccessoriesKit'

    def __str__(self):
        return self.kit_name


class AccessoriesKitItem(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_accKit_item",
                                   null=True, blank=True)
    accessory = models.ForeignKey(Accessories, on_delete=models.PROTECT, null=True,
                                  blank=True, related_name="kit_item_accessory")
    model = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    kit_item_price = models.DecimalField(
        max_digits=8, default=0, null=True, blank=True, decimal_places=2)
    quantity = models.DecimalField(
        max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    accessory_kit = models.ForeignKey(AccessoriesKit, on_delete=models.PROTECT, null=True,
                                      blank=True, related_name="item_accessory_kit")
    kit_item_total = models.DecimalField(
        max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    
    accessory_formula = models.CharField(max_length=225, null=True, blank=True)
    
    acce_divisions = models.BooleanField(default=False)

    class Meta:
        db_table = f'{TABLE_PREFIX}AccessoriesKitItem'
