
from django.db import models
from apps.Categories.models import Category
from apps.brands.models import CategoryBrands
from apps.product_master.models import Product
from apps.profiles.models import ProfileMasterSeries, ProfileMasterType, Profiles

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Parts(BaseModel):
    parts_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="parts_created_by")
    parts_category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="parts_category", null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Product_Parts'

    def __str__(self):
        return self.parts_name


class Profile_Kit(models.Model):
    product = models.ForeignKey(
        Product, blank=True, null=True, on_delete=models.PROTECT, related_name="parts_kit")
    profile_name = models.CharField(max_length=225, null=True, blank=True)
    kit_weight_lm = models.DecimalField(
        max_digits=8, decimal_places=3, default=0,  null=True, blank=True)
    system = models.ForeignKey(CategoryBrands, blank=True, null=True,
                              on_delete=models.PROTECT, related_name="profile_system")
    profile_type = models.ForeignKey(ProfileMasterType, on_delete=models.PROTECT, related_name="profile_kit_type", null=True, blank=True)
    profile_series = models.ForeignKey(ProfileMasterSeries, on_delete=models.PROTECT, related_name="profile_kit_series", null=True, blank=True)
    parts_kit = models.ForeignKey('product_parts.Product_Parts_Kit', blank=True, null=True,
                                  on_delete=models.PROTECT, related_name="profile_items_kit")
    class Meta:
        db_table = f'{TABLE_PREFIX}Profile_Kit'
    
    def __str__(self):
        return self.profile_series.profile_master_series


class Profile_items(models.Model):
    profile = models.ForeignKey(Profiles, blank=True, null=True,
                                on_delete=models.PROTECT, related_name="profile_item")
    profile_kit = models.ForeignKey(Profile_Kit, blank=True, null=True,
                                  on_delete=models.PROTECT, related_name="profile_items_kit")
    parts = models.ForeignKey('product_parts.Product_Parts_Kit_Items', blank=True, null=True,
                              on_delete=models.PROTECT, related_name="profile_part")
    thickness = models.CharField(max_length=225, blank=True, null=True)
    weight_per_lm = models.CharField(max_length=255, null=True, blank=True)
    
    formula = models.CharField(max_length=225, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Profile_items'


class Product_Parts_Kit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_parts_kit", blank=True, null=True)
    kit_name = models.CharField(max_length=225)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Product_Parts_Kit'
        
    def __str__(self):
        return self.kit_name


class Product_Parts_Kit_Items(models.Model):
    parts = models.ForeignKey(Parts, blank=True, null=True, on_delete=models.PROTECT, related_name="product_kit_parts")
    formula = models.CharField(max_length=225)
    product_parts_kit = models.ForeignKey(Product_Parts_Kit, blank=True, null=True, on_delete=models.PROTECT, related_name="product_kit_item")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Product_Parts_Kit_Items'
    