from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.accessories_kit.models import AccessoriesKit
from apps.brands.models import CategoryBrands
from apps.product_master.models import Product
from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from amoeba.settings import TABLE_PREFIX


class PanelMasterBase(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_panel_base",
                                   null=True, blank=True)
    panel_category = models.OneToOneField(Category, on_delete=models.PROTECT, unique=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}PanelMasterBase'

    def __str__(self):
        return self.panel_category.category


class PanelMasterBrands(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_panel_brands",
                                   null=True, blank=True)
    panel_category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="panel_category", null=True, blank=True)
    panel_brands = models.ForeignKey(CategoryBrands, on_delete=models.PROTECT)

    class Meta:
        db_table = f'{TABLE_PREFIX}PanelMasterBrands'

    def __str__(self):
        return self.panel_brands.brands.brand_name


class PanelMasterSeries(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_panel_series",
                                   null=True, blank=True)
    brands = models.ForeignKey(PanelMasterBrands, on_delete=models.PROTECT, related_name="panel_brand", null=True, blank=True)
    series = models.CharField(max_length=255)

    class Meta:
        db_table = f'{TABLE_PREFIX}PanelMasterSeries'

    def __str__(self):
        return self.series


class PanelMasterSpecifications(BaseModel):

    GLASS_TYPE = [
        (1, 'Double Glass Unit'),
        (2, 'Single Glass')
    ]

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_panel_specifications",
                                   null=True, blank=True)
    series = models.ForeignKey(PanelMasterSeries, on_delete=models.PROTECT, related_name="panel_series",
                               null=True, blank=True)
    specifications = models.CharField(max_length=500, null=True, blank=True)
    glass_type = models.IntegerField(choices=GLASS_TYPE, default=0, null=True, blank=True)
    outer = models.CharField(max_length=500, null=True, blank=True)
    air_space = models.CharField(max_length=500, null=True, blank=True)
    inner = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}PanelMasterSpecifications'

    def __str__(self):
        return self.specifications


class PanelMasterConfiguration(BaseModel):
    STATUS = [
        (1, 'Active'),
        (2, 'Inactive')
    ]

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_panel_config",
                                   null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
    date = models.DateTimeField()
    price_per_sqm = models.DecimalField(max_digits=9, default=0, decimal_places=2, null=True, blank=True)
    min_price_and_area_req = models.BooleanField(default=False, null=True, blank=True)
    min_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    min_area = models.DecimalField(default=1, max_digits=9, decimal_places=2, null=True, blank=True)
    markup_percentage_req = models.BooleanField(default=False, null=True, blank=True)
    markup_percentage = models.FloatField(validators=[MinValueValidator(0.0)],default=0, null=True, blank=True)
    # markup_percentage = models.FloatField(validators=[MinValueValidator(0.0),
    #                                                                        MaxValueValidator(100.0)],default=0, null=True, blank=True)
    panel_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                            related_name="panel_master_specification", null=True, blank=True)
    u_value = models.DecimalField(max_digits=9, default=0, decimal_places=2, null=True, blank=True)
    shading_coefficient = models.DecimalField(max_digits=9, default=0, decimal_places=2, null=True, blank=True)

    panel_quoted_rate = models.DecimalField(max_digits=9, default=0, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}PanelMasterConfiguration'

