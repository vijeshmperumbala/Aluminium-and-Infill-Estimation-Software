from datetime import timedelta
import django
from django.core.validators import MinValueValidator
from django.db import models

from apps.Categories.models import Category
from apps.others.models import SubmittingParameters
from apps.project_specifications.models import ProjectSpecifications
from apps.accessories_kit.models import AccessoriesKit, AccessoriesKitItem
from apps.addon_master.models import Addons
from apps.brands.models import CategoryBrands
from apps.configuration_master.models import ConfigurationsMaster
from apps.enquiries.models import (
    EnquirySpecifications, 
    Estimations, 
    Temp_EnquirySpecifications, 
    Temp_Estimations,
)
from apps.customers.models import Customers, Contacts
from apps.helper import one_month
from apps.panels_and_others.models import (
    PanelMasterSpecifications, 
    PanelMasterBrands, 
    PanelMasterSeries,
)
from apps.pricing_master.models import Sealant_kit, Surface_finish_kit
from apps.product_master.models import Product
from apps.product_parts.models import Profile_Kit
from apps.provisions.models import Provisions
from apps.quotations_master.models import Quotations_Master
from apps.rating.models import RatingHead
from apps.signatures.models import Signatures
from apps.suppliers.models import BillofQuantity, Suppliers
from apps.user.models import BaseModel, User
from apps.UoM.models import UoM

from amoeba.settings import TABLE_PREFIX


class EstimationManiVersion(BaseModel):
    version_text = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationManiVersion'
        
    def __int__(self):
        return self.version_text
    
    
class EstimationVersions(BaseModel):
    STATUS = [
        (1, 'Active'),
        (2, 'In Progress'), 
        (3, 'Management Review'),
        (4, 'Re-Estimating'), #Re-Estimating
        (5, 'Quotation On Hold'),
        (6, 'Approved'),
        (7, 'Inactive'),
        # (8, 'Revision'),
        (9, 'Estimating'),
        (10, 'Quote'),
        # (11, 'Drop'),
        (12, 'Quotation Sent'),
        (13, 'Customer Approved'),
        (14, 'Recalled'), 
        (15, 'Approved with Signature'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_enquiry_revision")
    version = models.CharField(max_length=20, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1, null=True, blank=True)
    main_version = models.ForeignKey(EstimationManiVersion, on_delete=models.CASCADE, null=True, blank=True, related_name="enquiry_version")

    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationVersions'

    # def __str__(self):
    #     return self.version

    # def __int__(self):
    #     return self.status


class EstimationBuildings(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_estimation_building")
    estimation = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name="estimation_building")
    building_name = models.CharField(max_length=255)
    no_typical_buildings = models.IntegerField(default=0, null=True, blank=True)
    typical_buildings_enabled = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationBuildings'

    def __str__(self):
        return self.building_name


class Temp_EstimationBuildings(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_estimation_building_temp")
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.PROTECT)
    building_name = models.CharField(max_length=255)
    no_typical_buildings = models.IntegerField(default=0, null=True, blank=True)
    typical_buildings_enabled = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    class Meta:
        db_table = TABLE_PREFIX + 'Temp_EstimationBuildings'

    def __str__(self):
        return self.building_name


class EstimationMainProduct(BaseModel):
    TOLERANCE = [
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]
    TYPE = [
        (1, 'Main Product'),
        (2, 'Associated Product'),
    ]
    
    DEDUCTION_TYPE = [
        (1, 'SqM'),
        (2, 'Non-SqM'),
    ]
    
    DEDUCTION_METHOD = [
        (1, "partial"),
        (2, "full"),
        (3, "merge"),
    ]

    building = models.ForeignKey(EstimationBuildings, on_delete=models.CASCADE, null=True, blank=True, related_name="main_product_building", db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="main_product_category")
    specification_Identifier = models.ForeignKey(EnquirySpecifications, on_delete=models.CASCADE, 
                                                 related_name="main_product_specification_identifier", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='main_product_product', null=True, blank=True)
    product_type = models.IntegerField(choices=TYPE, default=1, null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='main_product_glass_product', null=True, blank=True)
    
    main_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(CategoryBrands, on_delete=models.CASCADE,
                                           related_name='main_product_brand', null=True, blank=True)
    series = models.ForeignKey(Profile_Kit, on_delete=models.CASCADE,
                                           related_name='main_product_series', null=True, blank=True)
    associated_key = models.CharField(max_length=100, null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.CASCADE,
                              related_name='main_product_panel_brand', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.CASCADE,
                               related_name='main_product_panel_series', null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.CASCADE,
                                           related_name='main_product_uom', null=True, blank=True)
    accessories = models.ForeignKey(AccessoriesKit, on_delete=models.CASCADE,
                                           related_name='main_product_accessory', null=True, blank=True)
    is_accessory = models.BooleanField(default=True)
    accessory_quantity = models.IntegerField(null=True, blank=True, default=1)
    accessory_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    is_tolerance = models.BooleanField(default=False, null=True, blank=True)
    tolerance_type = models.IntegerField(choices=TOLERANCE, null=True, blank=True)
    tolerance = models.CharField(max_length=50, default=0, null=True, blank=True)
    total_addon_cost = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    is_sourced = models.BooleanField(default=False, null=True, blank=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                           related_name='main_product_suppliers', null=True, blank=True)
    boq_number = models.ForeignKey(BillofQuantity, on_delete=models.CASCADE,
                                           related_name='main_product_boq', null=True, blank=True)
    enable_addons = models.BooleanField(default=False, null=True, blank=True)
    is_display_data = models.BooleanField(default=False, null=True, blank=True)
    display_product_name = models.CharField(max_length=225, null=True, blank=True)
    display_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_total_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    hide_dimension = models.BooleanField(default=False, null=True, blank=True)
    total_associated_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    after_deduction_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    deduction_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    deduction_type = models.IntegerField(choices=DEDUCTION_TYPE, null=True, blank=True)
    deduction_method = models.IntegerField(choices=DEDUCTION_METHOD, null=True, blank=True)
    deducted_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    product_unit_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    product_sqm_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_sqm_price_without_addon = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_base_rate = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    have_merge = models.BooleanField(default=False)
    merge_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    minimum_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    convert_to_sales = models.BooleanField(default=False)
    # ordering = models.PositiveSmallIntegerField()
    disabled = models.BooleanField(default=False)
    product_index = models.IntegerField(null=True, blank=True)
    
    class Meta:
        # ordering = ['ordering']
        db_table = TABLE_PREFIX + 'EstimationMainProduct'
    
    def save(self, *args, **kwargs):
        if not self.display_product_name:
            if self.product:
                self.display_product_name = self.product.product_name
            elif self.panel_product:
                self.display_product_name = self.panel_product.product_name
        super().save(*args, **kwargs)


class Temp_EstimationMainProduct(BaseModel):
    TOLERANCE = [
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]
    TYPE = [
        (1, 'Main Product'),
        (2, 'Associated Product'),
    ]
    DEDUCTION_TYPE = [
        (1, 'SqM'),
        (2, 'Non-SqM'),
    ]
    
    DEDUCTION_METHOD = [
        (1, "partial"),
        (2, "full"),
        (3, "merge"),
    ]

    building = models.ForeignKey(Temp_EstimationBuildings, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation_temp")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="main_product_category_temp")
    specification_Identifier = models.ForeignKey(Temp_EnquirySpecifications, on_delete=models.CASCADE, related_name="main_product_specification_identifier_temp", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='main_product_product_temp', null=True, blank=True)
    product_type = models.IntegerField(choices=TYPE, default=1, null=True, blank=True)
    panel_product = models.ForeignKey(Product, default='0', on_delete=models.CASCADE,
                                           related_name='main_product_glass_product_temp', null=True, blank=True)
    main_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(CategoryBrands, on_delete=models.CASCADE,
                                           related_name='main_product_brand_temp', null=True, blank=True)
    series = models.ForeignKey(Profile_Kit, on_delete=models.CASCADE,
                                           related_name='main_product_series_temp', null=True, blank=True)
    associated_key = models.CharField(max_length=100, null=True, blank=True)
    
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.CASCADE,
                              related_name='main_product_panel_brand_temp', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.CASCADE,
                               related_name='main_product_panel_series_temp', null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.CASCADE,
                                           related_name='main_product_uom_temp', null=True, blank=True)
    accessories = models.ForeignKey(AccessoriesKit, on_delete=models.CASCADE,
                                           related_name='main_product_accessory_temp', null=True, blank=True)
    is_accessory = models.BooleanField(default=True)
    accessory_quantity = models.IntegerField(null=True, blank=True, default=1)
    accessory_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    is_tolerance = models.BooleanField(default=False, null=True, blank=True)
    tolerance_type = models.IntegerField(choices=TOLERANCE, null=True, blank=True)
    tolerance = models.CharField(max_length=50, default=0, null=True, blank=True)
    total_addon_cost = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)

    is_sourced = models.BooleanField(default=False, null=True, blank=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                           related_name='main_product_suppliers_temp', null=True, blank=True)
    boq_number = models.ForeignKey(BillofQuantity, on_delete=models.CASCADE,
                                           related_name='main_product_boq_temp', null=True, blank=True)
    enable_addons = models.BooleanField(default=False, null=True, blank=True)
    
    is_display_data = models.BooleanField(default=False, null=True, blank=True)
    display_product_name = models.CharField(max_length=225, null=True, blank=True)
    display_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    display_total_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    hide_dimension = models.BooleanField(default=False, null=True, blank=True)
    total_associated_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    after_deduction_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    deduction_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    deduction_type = models.IntegerField(choices=DEDUCTION_TYPE, null=True, blank=True)
    deduction_method = models.IntegerField(choices=DEDUCTION_METHOD, null=True, blank=True)
    
    deducted_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    product_unit_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    product_sqm_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    product_sqm_price_without_addon = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_base_rate = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    have_merge = models.BooleanField(default=False)
    merge_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    minimum_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    disabled = models.BooleanField(default=False)
    product_index = models.IntegerField(null=True, blank=True)
    
    
    class Meta:
        db_table = TABLE_PREFIX + 'Temp_EstimationMainProduct'

    def save(self, *args, **kwargs):
        if not self.display_product_name:
            if self.product:
                self.display_product_name = self.product.product_name
            elif self.panel_product:
                self.display_product_name = self.panel_product.product_name
        super().save(*args, **kwargs)
        

class MainProductAccessories(BaseModel):
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_accessory', null=True, blank=True, db_index=True)
    accessory_item = models.ForeignKey(AccessoriesKitItem, on_delete=models.PROTECT, related_name='accessory_item_in_kit', null=True, blank=True)
    accessory_item_quantity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    accessory_item_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    accessory_item_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)

    def remove_none(self):
        if not self.accessory_item_price and not self.accessory_item_total:
            if self.pk:
                # self.__class__.objects.get(pk=self.pk).delete()
                self.delete()

    def save(self, *args, **kwargs):
        self.remove_none()
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationMainProductAccessory'


class Temp_MainProductAccessories(BaseModel):
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_accessory_temp', null=True, blank=True, db_index=True)
    accessory_item = models.ForeignKey(AccessoriesKitItem, on_delete=models.PROTECT, related_name='accessory_item_in_kit_temp', null=True, blank=True)
    accessory_item_quantity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    accessory_item_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    accessory_item_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)

    def remove_none(self):
        if not self.accessory_item_price and not self.accessory_item_total:
            self.__class__.objects.get(pk=self.pk).delete()

    def save(self, *args, **kwargs):
        self.remove_none()
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EstimationMainProductAccessory'


class MainProductAluminium(BaseModel):
    UNIT = [
        (1, 'Pricing for SqM'),
        (2, 'Pricing for Unit'),
        (3, 'Pricing for KG'),
    ]

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
        (4, 'Formula Based'),
    ]

    PRE_PRICE = [
        (1, 'price_per_unit'),
        (2, 'price_per_sqm'),
        (3, 'weight_per_unit'),
    ]

    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_aluminium', null=True, blank=True, db_index=True)

    aluminium_pricing = models.IntegerField(choices=PRICING_TYPE, default=3, null=True, blank=True)
    al_price_per_unit = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    al_price_per_sqm = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    al_weight_per_unit = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    formula_base = models.BooleanField(default=False)
    al_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    pricing_unit = models.IntegerField(choices=UNIT, null=True, blank=True)
    custom_price = models.DecimalField(max_digits=20, default=0, decimal_places=2, null=True, blank=True)
    al_quoted_price = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    enable_divisions = models.BooleanField(default=False, null=True, blank=True)
    horizontal = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    vertical = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    curtainwall_type = models.BooleanField(default=False)
    is_conventional = models.BooleanField(default=False)
    is_two_way = models.BooleanField(default=False)
    total_linear_meter = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    weight_per_lm = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, default=0, blank=True)
    total_weight = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    product_description = models.CharField(max_length=255, null=True, blank=True)
    price_per_kg = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    weight_per_unit = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_configuration = models.ForeignKey(ConfigurationsMaster, on_delete=models.PROTECT, null=True, blank=True)
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, null=True, blank=True, related_name='aluminium_surface_finish')
    total_quantity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    in_area_input = models.BooleanField(default=False)

    class Meta:
        db_table = f'{TABLE_PREFIX}MainProductAluminium'


class Temp_MainProductAluminium(BaseModel):
    UNIT = [
        (1, 'Pricing for SqM'),
        (2, 'Pricing for Unit'),
        (3, 'Pricing for KG'),
    ]

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
        (4, "Formula Based"),
    ]

    PRE_PRICE = [
        (1, 'price_per_unit'),
        (2, 'price_per_sqm'),
        (3, 'weight_per_unit'),
    ]

    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_aluminium_temp', null=True, blank=True, db_index=True)
    aluminium_pricing = models.IntegerField(choices=PRICING_TYPE, default=3, null=True, blank=True)
    al_price_per_unit = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    al_price_per_sqm = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    al_weight_per_unit = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    formula_base = models.BooleanField(default=False)
    al_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    pricing_unit = models.IntegerField(choices=UNIT, null=True, blank=True)
    custom_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    al_quoted_price = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    enable_divisions = models.BooleanField(default=False, null=True, blank=True)
    horizontal = models.DecimalField(max_digits=30, decimal_places=2, default=0,  null=True, blank=True)
    vertical = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    curtainwall_type = models.BooleanField(default=False)
    is_conventional = models.BooleanField(default=False)
    is_two_way = models.BooleanField(default=False)
    total_linear_meter = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    weight_per_lm = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    product_description = models.CharField(max_length=255, null=True, blank=True)
    price_per_kg = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    weight_per_unit = models.DecimalField(max_digits=30, decimal_places=2,  default=0, null=True, blank=True)
    product_configuration = models.ForeignKey(ConfigurationsMaster, on_delete=models.PROTECT, null=True, blank=True)
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, null=True, blank=True, related_name='aluminium_surface_finish_temp')
    total_quantity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    in_area_input = models.BooleanField(default=False)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_MainProductAluminium'


class MainProductGlass(BaseModel):
    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_glass', null=True, blank=True, db_index=True)
    is_glass_cost = models.BooleanField(default=False, null=True, blank=True)
    glass_specif = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                           related_name='main_product_glass_specifi', null=True, blank=True)
    total_area_glass = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_base_rate = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_markup_percentage = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    glass_quoted_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_pricing_type = models.IntegerField(choices=PRICING_TYPE, default=3, null=True, blank=True)
    glass_price_per_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_primary = models.BooleanField(default=True, null=True, blank=True)
    glass_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_quantity = models.IntegerField(default=1, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}MainProductGlass'
    
    def __str__(self):
        return str(self.glass_specif)


class Temp_MainProductSecondtaryGlass(BaseModel):
    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_temp_secondary_glass', null=True, blank=True, db_index=True)
    sec_is_glass_cost = models.BooleanField(default=False, null=True, blank=True)
    sec_glass_specif = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                           related_name='main_product_temp_secondary_glass_specifi', null=True, blank=True)
    sec_base_rate = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    sec_markup_percentage = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    sec_quoted_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    sec_glass_pricing_type = models.IntegerField(choices=PRICING_TYPE, default=3, null=True, blank=True)
    sec_price_per_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='main_product_temp_secondary_glass_user', null=True, blank=True)
    sec_glass_primary = models.BooleanField(default=True, null=True, blank=True)
    sec_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    sec_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    sec_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    sec_quantity = models.IntegerField(default=1, null=True, blank=True)
    sec_total_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_MainProductSecondaryGlass'
        
    def __str__(self):
        return self.glass_specif


class Temp_MainProductGlass(BaseModel):
    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]
    

    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_glass_temp', null=True, blank=True, db_index=True)
    is_glass_cost = models.BooleanField(default=False, null=True, blank=True)
    glass_specif = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                           related_name='main_product_glass_specifi_temp', null=True, blank=True)
    total_area_glass = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_base_rate = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_markup_percentage = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    glass_quoted_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_pricing_type = models.IntegerField(choices=PRICING_TYPE, null=True, blank=True)
    glass_price_per_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_primary = models.BooleanField(default=True, null=True, blank=True)
    glass_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    glass_quantity = models.IntegerField(default=1, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_MainProductGlass'
   
        
class MainProductSilicon(BaseModel):
    
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_silicon', null=True, blank=True, db_index=True)
    is_silicon = models.BooleanField(default=True, null=True, blank=True)
    external_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    external_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    external_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    external_sealant_type = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_external_sealant',null=True, blank=True)
    internal_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    internal_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    internal_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    internal_sealant_type = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_internal_sealant',null=True, blank=True)
    silicon_quoted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    polyamide_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_polyamide_gasket',null=True, blank=True)
    polyamide_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    polyamide_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    polyamide_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    transom_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_transom_gasket',null=True, blank=True)
    transom_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    transom_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    transom_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    mullion_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_mullion_gasket',null=True, blank=True)
    mullion_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    mullion_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    mullion_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}MainProductSilicon'
   
    
class Temp_MainProductSilicon(BaseModel):
    
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_silicon_temp', null=True, blank=True, db_index=True)
    is_silicon = models.BooleanField(default=True, null=True, blank=True)
    external_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    external_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    external_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    external_sealant_type = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_external_sealant_temp',null=True, blank=True)
    internal_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    internal_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    internal_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    internal_sealant_type = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_internal_sealant_temp',null=True, blank=True)
    silicon_quoted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    polyamide_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_polyamide_gasket_temp',null=True, blank=True)
    polyamide_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    polyamide_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    polyamide_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    transom_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_transom_gasket_temp',null=True, blank=True)
    transom_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    transom_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    transom_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    mullion_gasket = models.ForeignKey(Sealant_kit, on_delete=models.PROTECT, related_name='main_product_mullion_gasket_temp',null=True, blank=True)
    mullion_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    mullion_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    mullion_lm = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_MainProductSilicon'


class Deduction_Items(BaseModel):
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT, related_name='main_product_deduction_items', null=True, blank=True, db_index=True)
    item_desc = models.ForeignKey(MainProductGlass, on_delete=models.PROTECT, related_name='main_product_deduction_item', null=True, blank=True)
    main_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    item_width = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_height = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_quantity = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_deduction_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_deduction_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationMainProduct_Deduction_Items'


class Temp_Deduction_Items(BaseModel):
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT, related_name='temp_main_product_deduction_items', null=True, blank=True, db_index=True)
    item_desc = models.ForeignKey(Temp_MainProductGlass, on_delete=models.PROTECT, related_name='temp_main_product_deduction_item', null=True, blank=True)
    main_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    item_width = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_height = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_quantity = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_deduction_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    item_deduction_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EstimationMainProduct_Deduction_Items'
      
        
class EstimationMainProductMergeData(models.Model):
    
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='main_product_merge', null=True, blank=True, db_index=True)
    merge_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='merge_product', null=True, blank=True)
    merged_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merged_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_quantity = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_aluminium_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_infill_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_sealant_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_accessory_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationMainProduct_MergeData'
        

class Temp_EstimationMainProductMergeData(models.Model):
    
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='temp_main_product_merge', null=True, blank=True, db_index=True)
    merge_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT,
                                           related_name='temp_merge_product', null=True, blank=True)
    merged_area = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merged_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_quantity = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_aluminium_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_infill_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_sealant_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    merge_accessory_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EstimationMainProduct_MergeData'
        
        
class MainProductAddonCost(BaseModel):
    PRICING_TYPE = [
        (1, 'Price per Linear Meter'),
        (2, 'Price per Square Meter'),
        (3, 'Price per Unit')
    ]
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT, null=True, blank=True, related_name='mainproduct_addons', db_index=True)
    addons = models.ForeignKey(Addons, on_delete=models.PROTECT, null=True, blank=True)
    pricing_type = models.IntegerField(choices=PRICING_TYPE, null=True, blank=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    addon_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}MainProductAddonCost'


class Temp_MainProductAddonCost(BaseModel):
    PRICING_TYPE = [
        (1, 'Price per Linear Meter'),
        (2, 'Price per Square Meter'),
        (3, 'Price per Unit')
    ]
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    addons = models.ForeignKey(Addons, on_delete=models.PROTECT, null=True, blank=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    pricing_type = models.IntegerField(choices=PRICING_TYPE, null=True, blank=True)
    addon_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_MainProductAddonCost'
        

class PricingOption(BaseModel):
    estimation_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT, null=True, blank=True, related_name='estimate_main_pricingoption', db_index=True)
    is_pricing_control = models.BooleanField(default=False, null=True, blank=True)
    overhead_perce = models.DecimalField(max_digits=100, decimal_places=20, default=0, null=True, blank=True)
    labour_perce = models.DecimalField(max_digits=100, decimal_places=20, default=0, null=True, blank=True)
    adjust_by_sqm = models.BooleanField(default=False)

    class Meta:
        db_table = f'{TABLE_PREFIX}PricingOption'
        

class Temp_PricingOption(BaseModel):
    estimation_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT, null=True, blank=True, related_name='temp_estimate_main_pricingoption', db_index=True)
    is_pricing_control = models.BooleanField(default=False, null=True, blank=True)
    overhead_perce = models.DecimalField(max_digits=100, decimal_places=20, default=0, null=True, blank=True)
    labour_perce = models.DecimalField(max_digits=100, decimal_places=20, default=0, null=True, blank=True)
    adjust_by_sqm = models.BooleanField(default=False)

    class Meta:
        db_table = f'{TABLE_PREFIX}Tepm_PricingOption'


class Quotations(BaseModel):
    TYPE = [
        (1, 'General'),
        (2, 'Short'),
    ]
    
    
    DISCOUNT_TYPE = [
        (0, 'None'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]

    estimations = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='estimation_quotations', db_index=True)
    estimations_version = models.ForeignKey(EstimationVersions, on_delete=models.PROTECT, related_name='enquiry_versions_quotations')
    quotation_id = models.CharField(max_length=225)
    quotation_date = models.DateTimeField(default=django.utils.timezone.now)
    valid_till = models.DateTimeField(default=one_month())
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_quotation")
    q_type = models.IntegerField(choices=TYPE, default=1, null=True, blank=True)
    remarks = models.CharField(max_length=5000, null=True, blank=True)
    prepared_for = models.ManyToManyField(Customers, related_name='quotation_prepared_customers')
    quotation_customer = models.ForeignKey(Customers, on_delete=models.PROTECT, related_name='quotation_customer', null=True, blank=True)
    represented_by = models.ForeignKey(Contacts, on_delete=models.PROTECT, related_name='quotation_represent_customers', null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    products_specifications = models.CharField(max_length=5000, null=True, blank=True)
    terms_of_payment = models.CharField(max_length=5000, null=True, blank=True)
    exclusions = models.CharField(max_length=5000, null=True, blank=True)
    terms_and_conditions = models.CharField(max_length=10000, null=True, blank=True)
    signature = models.ForeignKey(Signatures, on_delete=models.PROTECT, null=True, blank=True)
    
    discount_type = models.IntegerField(choices=DISCOUNT_TYPE, default=0, null=True, blank=True)
    apply_total = models.BooleanField(default=True, null=True, blank=True)
    apply_line_items = models.BooleanField(default=False, null=True, blank=True)
    discount = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    quoatation_approval_number = models.CharField(max_length=2, default=1, null=True, blank=True)
    custom_specifictaion = models.BooleanField(default=False, null=True, blank=True)

    template = models.ForeignKey(Quotations_Master, on_delete=models.PROTECT, null=True, blank=True, related_name='estimation_quotations_template')
    notes = models.CharField(max_length=5000, null=True, blank=True)
    watermark = models.CharField(max_length=10, default="Draft", null=True, blank=True)
    building_total_enable = models.BooleanField(default=False, null=True, blank=True)
    quote_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    other_notes = models.CharField(max_length=10000, null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    is_provisions = models.BooleanField(default=False)
    is_dimensions = models.BooleanField(default=True)
    is_quantity = models.BooleanField(default=True)
    is_rpu = models.BooleanField(default=True)
    is_rpsqm = models.BooleanField(default=False)
    is_area = models.BooleanField(default=False)
    display_discount_perc = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Quotations'
        

class Quotation_Provisions(models.Model):
    quotation = models.ForeignKey(Quotations, on_delete=models.PROTECT, related_name='estimation_quotation')
    provision = models.ForeignKey(Provisions, on_delete=models.PROTECT, related_name='provision_type')
    provision_cost = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Quotation_Provisions'
        
           
class Temp_Quotations(BaseModel):
   
    TYPE = [
        (1, 'General'),
        (2, 'Short'),
    ]
    
    DISCOUNT_TYPE = [
        (0, 'None'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]

    estimations = models.ForeignKey(Temp_Estimations, on_delete=models.CASCADE, related_name='temp_estimation_quotations', db_index=True)
    estimations_version = models.ForeignKey(EstimationVersions, on_delete=models.CASCADE, related_name='temp_enquiry_versions_quotations')
    quotation_id = models.CharField(max_length=225)
    quotation_date = models.DateTimeField(default=django.utils.timezone.now)
    valid_till = models.DateTimeField(default=one_month())
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="temp_created_by_quotation")
    q_type = models.IntegerField(choices=TYPE, default=1, null=True, blank=True)
    remarks = models.CharField(max_length=5000, null=True, blank=True)
    prepared_for = models.ManyToManyField(Customers, related_name='temp_quotation_prepared_customers')
    quotation_customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='temp_quotation_customer', null=True, blank=True)
    represented_by = models.ForeignKey(Contacts, on_delete=models.CASCADE, related_name='temp_quotation_represent_customers', null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    products_specifications = models.CharField(max_length=5000, null=True, blank=True)
    terms_of_payment = models.CharField(max_length=10000, null=True, blank=True)
    exclusions = models.CharField(max_length=5000, null=True, blank=True)
    terms_and_conditions = models.CharField(max_length=10000, null=True, blank=True)
    signature = models.ForeignKey(Signatures, on_delete=models.CASCADE, null=True, blank=True)
    discount_type = models.IntegerField(choices=DISCOUNT_TYPE, default=0, null=True, blank=True)
    apply_total = models.BooleanField(default=True, null=True, blank=True)
    apply_line_items = models.BooleanField(default=False, null=True, blank=True)
    discount = models.FloatField(validators=[MinValueValidator(0.0)], null=True, blank=True)
    quoatation_approval_number = models.CharField(max_length=2, null=True, blank=True)
    custom_specifictaion = models.BooleanField(default=False, null=True, blank=True)
    template = models.ForeignKey(Quotations_Master, on_delete=models.PROTECT, null=True, blank=True, related_name='temp_estimation_quotations_template')
    notes = models.CharField(max_length=5000, null=True, blank=True)
    watermark = models.CharField(max_length=10, default="Draft", null=True, blank=True)
    building_total_enable = models.BooleanField(default=False, null=True, blank=True)
    quote_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    other_notes = models.CharField(max_length=10000, null=True, blank=True)
    is_draft = models.BooleanField(default=True)    
    is_provisions = models.BooleanField(default=False)
    is_dimensions = models.BooleanField(default=True)
    is_quantity = models.BooleanField(default=True)
    is_rpu = models.BooleanField(default=True)
    is_rpsqm = models.BooleanField(default=False)
    is_area = models.BooleanField(default=False)
    display_discount_perc = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Quotations'
       
        
class Temp_Quotation_Provisions(models.Model):
    quotation = models.ForeignKey(Temp_Quotations, null=True, blank=True, on_delete=models.PROTECT, related_name='temp_estimation_quotation')
    provision = models.ForeignKey(Provisions, on_delete=models.PROTECT, related_name='temp_provision_type')
    provision_cost = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Quotation_Provisions'
        
        
class ProductCategoryRemarks(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_remark")
    product = models.ForeignKey(EstimationMainProduct, on_delete=models.CASCADE, related_name='estimation_product')
    remark = models.CharField(max_length=1000, null=True, blank=True)
    acknowledgement = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProductCategoryRemarks'
        
    
class EstimationProductComplaints(BaseModel):
    estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name="estimation_product_complaints", null=True, blank=True)
    specification = models.ForeignKey(EnquirySpecifications, on_delete=models.CASCADE, related_name="enquiry_specification")
    is_aluminium_complaint = models.BooleanField(default=False, null=True, blank=True)
    aluminium_complaint = models.CharField(max_length=1000, null=True, blank=True)
    is_panel_complaint = models.BooleanField(default=False, null=True, blank=True)
    panel_complaint = models.CharField(max_length=1000, null=True, blank=True)
    is_surface_finish_complaint = models.BooleanField(default=False, null=True, blank=True)
    surface_finish_complaint = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationProductComplaints'


class Temp_EstimationProductComplaints(BaseModel):
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.CASCADE, related_name="estimation_product_complaints", null=True, blank=True)
    specification = models.ForeignKey(Temp_EnquirySpecifications, on_delete=models.CASCADE, related_name="enquiry_specification")
    is_aluminium_complaint = models.BooleanField(default=False, null=True, blank=True)
    aluminium_complaint = models.CharField(max_length=1000, null=True, blank=True)
    is_panel_complaint = models.BooleanField(default=False, null=True, blank=True)
    panel_complaint = models.CharField(max_length=1000, null=True, blank=True)
    is_surface_finish_complaint = models.BooleanField(default=False, null=True, blank=True)
    surface_finish_complaint = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EstimationProductComplaints'


class Quote_Send_Detail(BaseModel):
    STATUS = [
        (1, 'By Hand'),
        (2, 'By Email'),
        (3, 'By Fax'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_quotation_send")
    quotation = models.ForeignKey(Quotations, on_delete=models.PROTECT, related_name='quotation_send_quotation')
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    send_date = models.DateTimeField() #default=django.utils.timezone.now
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Quote_Send_Detail'


class ProductComments(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_product_comment")
    product = models.ForeignKey(EstimationMainProduct, on_delete=models.CASCADE, related_name='estimation_product_comment')
    comment = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}ProductComments'
        

class Temp_ProductComments(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_product_comment_temp")
    product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.CASCADE, related_name='estimation_product_comment_temp')
    comment = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_ProductComments'


class EstimationProduct_Associated_Data(models.Model):
    estimation_main_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    associated_product = models.ForeignKey(EstimationMainProduct,on_delete=models.CASCADE, related_name='associated_product', null=True, blank=True)
    is_sync = models.BooleanField(default=False)
    associated_qunaty = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    assoicated_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    is_deducted = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationProduct_Associated_Data'
        

class Temp_EstimationProduct_Associated_Data(models.Model):
    estimation_main_product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    associated_product = models.ForeignKey(Temp_EstimationMainProduct,on_delete=models.CASCADE, related_name='associated_product_temp', null=True, blank=True)
    is_sync = models.BooleanField(default=False)
    associated_qunaty = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    assoicated_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    is_deducted = models.BooleanField(default=False)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EstimationProduct_Associated_Data'


class Quotation_Notes(BaseModel):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="quotation_note_user")
    quotation_notes = models.CharField(max_length=2000)
    quotation = models.ForeignKey(Quotations, on_delete=models.CASCADE, related_name="quotation_notes")
    quote_value = models.CharField(max_length=20, null=True, blank=True)
    # tag = models.ForeignKey('tags.Tags', on_delete=models.PROTECT, null=True, blank=True, related_name='quotation_tag')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Quotation_Notes'


class Temp_Quotation_Notes(BaseModel):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="temp_quotation_note_user")
    quotation_notes = models.CharField(max_length=2000)
    quotation = models.ForeignKey(Temp_Quotations, on_delete=models.CASCADE, related_name="temp_quotation_notes")
    quote_value = models.CharField(max_length=20, null=True, blank=True)
    # tag = models.ForeignKey('tags.Tags', on_delete=models.PROTECT, related_name='temp_quotation_tag')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Quotation_Notes'


class Quotation_Notes_Comments(BaseModel):
    comments = models.CharField(max_length=225, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_notes_comments")
    quotation_note = models.ForeignKey(Quotation_Notes, on_delete=models.CASCADE, related_name="comments_quotation_notes")
    is_read = models.BooleanField(default=False)
    read_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='quotation_notes_comment_read_by')
    class Meta:
        db_table = TABLE_PREFIX + 'Quotation_Notes_Comments'


class Temp_Quotation_Notes_Comments(BaseModel):
    comments = models.CharField(max_length=225, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="temp_created_by_history_comments")
    quotation_note = models.ForeignKey(Temp_Quotation_Notes, on_delete=models.CASCADE, related_name="temp_comments_quotation_notes")
    is_read = models.BooleanField(default=False)
    read_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='quotation_notes_comment_read_by_temp')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Quotation_Notes_Comments'
      
        
class QuotationDownloadHistory(BaseModel):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="quotation_download_user")
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    quotation_data = models.ForeignKey(Quotations, null=True, blank=True, on_delete=models.CASCADE, related_name="quotation_download_history")
    quotation_customer = models.ForeignKey(Customers, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Quotation_Download_History'
        

class EstimationProjectSpecifications(BaseModel):
    specification_header = models.ForeignKey(ProjectSpecifications, on_delete=models.PROTECT, related_name='project_scope_in_estimation')
    estimations = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='estimation_project_scope')
    specification = models.CharField(max_length=1000)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Estimation_ProjectSpecifications'
        

class Temp_EstimationProjectSpecifications(BaseModel):
    specification_header = models.ForeignKey(ProjectSpecifications, on_delete=models.PROTECT, related_name='temp_project_scope_in_estimation')
    estimations = models.ForeignKey(Temp_Estimations, on_delete=models.PROTECT, related_name='temp_estimation_project_scope')
    specification = models.CharField(max_length=1000)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Estimation_ProjectSpecifications'
        
        
class Estimation_GeneralNotes(BaseModel):
    estimations = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='estimation_generalnote')
    general_notes = models.CharField(max_length=10000, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="estimation_general_notes_created")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Estimation_General_Notes'
        
        
class Temp_Estimation_GeneralNotes(BaseModel):
    estimations = models.ForeignKey(Temp_Estimations, on_delete=models.PROTECT, related_name='temp_estimation_generalnote')
    general_notes = models.CharField(max_length=10000, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="temp_estimation_general_notes_created")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Estimation_General_Notes'
        

class Estimation_Rating(BaseModel):
    
    estimations = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='estimation_rating')
    rating_parameter = models.ForeignKey(RatingHead, on_delete=models.PROTECT, related_name='estimation_rating_parameter')
    rating_count = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Estimation_Rating'
        
        
class EstimationSubmitting_Hours(BaseModel):
    estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name='estimation_in_submiting')
    parameter = models.ForeignKey(SubmittingParameters, on_delete=models.CASCADE, related_name='estimation_submitting_parameters')
    time_data = models.CharField(max_length=30, default="00:00:00", null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EstimationSubmitting_Hours'
        

class Estimation_UserTimes(models.Model):
    
    STATUS = [
        (1, 'Active'),
        (2, 'In Progress'), 
        (3, 'Management Review'),
        (4, 'Re-Estimating'), #Re-Estimating
        (5, 'Quotation On Hold'),
        (6, 'Approved'),
        (7, 'Inactive'),
        # (8, 'Revision'),
        (9, 'Estimating'),
        (10, 'Quote'),
        # (11, 'Drop'),
        (12, 'Quotation Sent'),
        (13, 'Customer Approved'),
        (14, 'Recalled'), 
        (15, 'Approved with Signature'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name="estimation_active_time")
    active_time = models.DurationField(default=timedelta(0))
    updated_at = models.DateTimeField(null=True, blank=True)
    last_update = models.CharField(max_length=8, default='00:00:00')
    date = models.DateField(default=django.utils.timezone.now)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}Estimation_UserTimes' 


class Temp_Estimation_UserTimes(models.Model):
    
    STATUS = [
        (1, 'Active'),
        (2, 'In Progress'), 
        (3, 'Management Review'),
        (4, 'Re-Estimating'), #Re-Estimating
        (5, 'Quotation On Hold'),
        (6, 'Approved'),
        (7, 'Inactive'),
        # (8, 'Revision'),
        (9, 'Estimating'),
        (10, 'Quote'),
        # (11, 'Drop'),
        (12, 'Quotation Sent'),
        (13, 'Customer Approved'),
        (14, 'Recalled'), 
        (15, 'Approved with Signature'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.CASCADE, related_name="temp_estimation_active_time")
    active_time = models.DurationField(default=timedelta(0))
    updated_at = models.DateTimeField(null=True, blank=True)
    last_update = models.CharField(max_length=8, default='00:00:00')
    date = models.DateField(default=django.utils.timezone.now)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Estimation_UserTimes' 
        
    
class AuditLogModel(models.Model):
    
    message = models.CharField(max_length=500)
    estimation = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='audit_log_estimation')
    product = models.ForeignKey(EstimationMainProduct, on_delete=models.CASCADE, related_name='audit_log_product')
    date_time = models.DateTimeField(default=django.utils.timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_log_user')
    module = models.CharField(max_length=225, null=True, blank=True)
    old_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}AuditLogModel' 


class Temp_AuditLogModel(models.Model):
    
    message = models.CharField(max_length=500)
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.PROTECT, related_name='temp_audit_log_estimation')
    product = models.ForeignKey(Temp_EstimationMainProduct, on_delete=models.CASCADE, related_name='temp_audit_log_product')
    date_time = models.DateTimeField(default=django.utils.timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='temp_audit_log_user')
    
    old_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_quantity = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_price = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    old_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    new_sqm = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    module = models.CharField(max_length=225, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_AuditLogModel' 
        
        
        