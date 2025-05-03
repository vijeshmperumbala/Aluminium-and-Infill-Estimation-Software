import django
from django.db import models

from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from amoeba.settings import TABLE_PREFIX


class Countries(models.Model):

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)

    class Meta:
        db_table = f'{TABLE_PREFIX}Countries'

    def __str__(self):
        return self.name


class CategoryBrands(BaseModel):

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_category_brand")
    brands = models.ForeignKey('brands.Brands', null=True, blank=True, on_delete=models.PROTECT, related_name="base_brand_cat")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="category_brand_cat")
    country = models.ForeignKey(Countries, on_delete=models.PROTECT, related_name="country_brand_cat")

    class Meta:
        db_table = f'{TABLE_PREFIX}CategoryBrands'

    def __str__(self):
        return self.brands.brand_name


class AccessoriesBrands(BaseModel):

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_accessory_brand")
    # brand = models.CharField(max_length=255)
    brands = models.ForeignKey('brands.Brands', null=True, blank=True, on_delete=models.PROTECT, related_name="base_brand_acce")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="accessory_brand_cat")
    country = models.ForeignKey(
        Countries, on_delete=models.PROTECT, related_name="country_accessory_cat")

    class Meta:
        db_table = f'{TABLE_PREFIX}AccessoriesBrands'

    def __str__(self):
        return self.brands.brand_name


class Brands(models.Model):
    
    brand_name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_base_brand")

    class Meta:
        db_table = f'{TABLE_PREFIX}BaseBrands'
        
    def __str__(self):
        return self.brand_name
    