from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.brands.models import CategoryBrands
from apps.product_master.models import Product
from apps.product_parts.models import Profile_Kit
from apps.profiles.models import ProfileMasterSeries
from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from amoeba.settings import TABLE_PREFIX


class ConfigurationMasterBase(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_config_master_base",
                                   null=True, blank=True)
    config_category = models.OneToOneField(
        Category, on_delete=models.PROTECT, unique=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}ConfigurationMasterBase'

    def __str__(self):
        return self.config_category.category


class ConfigurationMasterBrands(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_config_brand",
                                   null=True, blank=True)
    category = models.ForeignKey(ConfigurationMasterBase, on_delete=models.PROTECT,
                                 related_name="configuration_master_category", null=True, blank=True)
    config_products = models.ForeignKey(Product, on_delete=models.PROTECT,
                                        related_name="configuration_product", null=True, blank=True)
    brands = models.ForeignKey(CategoryBrands, on_delete=models.PROTECT,
                               related_name="configuration_brand")

    class Meta:
        db_table = f'{TABLE_PREFIX}ConfigurationMasterBrands'

    def __str__(self):
        return self.brands.brand


class ConfigurationMasterSeries(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_config_series",
                                   null=True, blank=True)
    config_brands = models.ForeignKey(ConfigurationMasterBrands, on_delete=models.PROTECT,
                                      related_name="configuration_series_brand", null=True, blank=True)
    config_series = models.ForeignKey(Profile_Kit, on_delete=models.PROTECT,
                                      related_name="configuration_series", null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}ConfigurationMasterSeries'


class ConfigurationsMaster(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_config_master",
                                   null=True, blank=True)
    config_series = models.ForeignKey(Profile_Kit, on_delete=models.PROTECT,
                                      related_name="configurations_series", null=True, blank=True)
    title = models.CharField(max_length=255)
    descriptions = models.CharField(max_length=255, null=True, blank=True)
    width = models.IntegerField(default=0, null=True, blank=True)
    height = models.IntegerField(default=0, null=True, blank=True)
    unit_area = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00, null=True, blank=True)
    weight_per_unit = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True)
    price_per_sqm = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True)
    price_per_unit = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True)
    min_price_and_area_req = models.BooleanField(default=False)
    min_price = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True)
    markup_percentage_req = models.BooleanField(default=False)
    markup_percentage = models.FloatField(default=0,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    enable_weight_per_unit = models.BooleanField(
        default=False, null=True, blank=True)
    enable_price_per_sqm = models.BooleanField(
        default=False, null=True, blank=True)
    enable_price_per_unit = models.BooleanField(
        default=False, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}ConfigurationsMaster'
