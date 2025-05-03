import django
from django.db import models
from apps.Workstations.models import Workstations
from apps.accessories_master.models import Accessories
from apps.associated_product.models import AssociatedProducts

from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from apps.UoM.models import UoM
from amoeba.settings import TABLE_PREFIX

STATUS = [
    (1, 'Published'),
    (2, 'Draft'),
    (3, 'Scheduled'),
    (4, 'Inactive')
]


class Product(BaseModel):
    
    PRODUCT_TYPE = [
        (1, "Primary"),
        (2, "Secondary"),
    ]

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_product", null=True, blank=True)
    product_name = models.CharField(max_length=255, unique=True)
    product_category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT)
    description = models.CharField(max_length=255, null=True, blank=True)
    effective_from = models.DateTimeField(default=django.utils.timezone.now)
    image = models.ImageField(upload_to='product/image', blank=True)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
    installation_hours = models.CharField(max_length=20, null=True, blank=True)
    fabrication_man_hours = models.CharField(max_length=20, null=True, blank=True)
    have_associated_product = models.BooleanField(default=False)
    associated_product = models.ForeignKey(AssociatedProducts, on_delete=models.PROTECT, null=True, blank=True, related_name='product_associated_product')
    have_infill = models.BooleanField(default=False)
    assocated_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    infill_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    quotation_product_name = models.CharField(max_length=50, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_type = models.IntegerField(choices=PRODUCT_TYPE, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Products'

    def __str__(self):
        return self.product_name


class Product_Accessories(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True)
    product_accessories_title = models.CharField(
        max_length=255, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Product_Accessories'

    def __str__(self):
        return self.product_accessories_title


class Product_Accessories_Kit(models.Model):

    accessory = models.ForeignKey(Accessories, on_delete=models.PROTECT, null=True,
                                  blank=True, related_name="product_base_kit_accessory")
    accessory_formula = models.CharField(max_length=255, blank=True, null=True)

    product_accessory = models.ForeignKey(
        Product_Accessories, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Product_Accessory_kit'


class Product_WorkStations(models.Model):
    
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.PROTECT, related_name='workshop_product')
    workstation = models.ForeignKey(Workstations, null=True, blank=True, on_delete=models.PROTECT, related_name='product_workstation')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Product_WorkStations'


class SecondaryProducts(models.Model):
    
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_by_secondary_product", null=True, blank=True)
    product_name = models.CharField(max_length=255, unique=True)
    product_category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='secondary_product/image', blank=True)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SecondaryProducts'

    def __str__(self):
        return self.product_name










