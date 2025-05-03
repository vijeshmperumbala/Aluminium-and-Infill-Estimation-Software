import django
from django.db import models
from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator, 
    FileExtensionValidator,
)
from apps.UoM.models import UoM

from apps.Workstations.models import Workstations
from apps.accessories_kit.models import AccessoriesKitItem
from apps.addon_master.models import Addons
from apps.associated_product.models import AssociatedProducts
from apps.companies.models import Companies
from apps.customers.models import Customers
from apps.enquiries.models import (
    Enquiries, 
    EnquirySpecifications, 
    Estimations,
)
from apps.estimations.models import (
    EstimationMainProduct, 
    MainProductGlass, 
    Quotations,
)
from apps.panels_and_others.models import (
    PanelMasterBase, 
    PanelMasterBrands, 
    PanelMasterSeries, 
    PanelMasterSpecifications,
)
from apps.pricing_master.models import Surface_finish_kit
from apps.product_parts.models import Parts, Profile_Kit
from apps.suppliers.models import Suppliers
from apps.surface_finish.models import SurfaceFinishColors
from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from apps.product_master.models import Product
from apps.brands.models import CategoryBrands
from apps.profiles.models import ProfileMasterType

from apps.vehicles_and_drivers.models import Drivers, Vehicles

from amoeba.settings import TABLE_PREFIX


class ProjectsModel(BaseModel):
    
    STATUS = [
        (1, 'Ongoing'),
        (2, 'Onhold'),
        (3, 'Drop'),
        (4, 'Completed'),
        (0, 'Test')
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    project_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID of the project")
    project_title = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the project")
    project_customer = models.ForeignKey(Customers, on_delete=models.PROTECT, null=True, blank=True, related_name="project_customer")
    # quotation = models.ManyToManyField(Quotations, symmetrical=False, related_name="project_quotation")
    project_image = models.ImageField(upload_to='project/image', null=True, blank=True)
    created_date = models.DateTimeField(blank=True, null=True, help_text="Created date")
    # estimations_version = models.ForeignKey(Estimations, on_delete=models.PROTECT, blank=True, null=True, related_name="estimations_version_id")
    due_date = models.DateTimeField(blank=True, null=True, help_text="Due date")
    status = models.IntegerField(choices=STATUS, default=1, null=True, help_text="Status of the project")

    class Meta:
        db_table = f'{TABLE_PREFIX}Projects'
       
       
class ProjectEstimations(models.Model):
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT,  related_name="main_project_data")
    enquiry = models.ForeignKey(Enquiries, on_delete=models.PROTECT, related_name="main_project_enquiry")
    estimations_version = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name="estimations_version_id")
    quotation = models.ForeignKey(Quotations, on_delete=models.PROTECT,  related_name="project_quotation")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProjectEstimations'
       
       
class SalesOrderGroups(models.Model):
    group_name = models.CharField(max_length=255)
    enquiry_data = models.ForeignKey(Enquiries, on_delete=models.PROTECT, related_name="salesorder_group_enquiry")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT,  related_name="salesorder_group_data")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesOrderGroups'


class SalesOrderSpecification(models.Model):
    
    reference_specification = models.ForeignKey(EnquirySpecifications, on_delete=models.PROTECT, related_name='salesorder_ref_specification', null=True, blank=True)
    identifier = models.CharField(max_length=50, null=True, blank=True)
    categories = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, related_name="salesorder_specif_category")
    aluminium_products = models.ForeignKey(Product, on_delete=models.PROTECT,
                                           related_name='salesorder_spec_system', null=True, blank=True)
    aluminium_system = models.ForeignKey(CategoryBrands, on_delete=models.PROTECT,
                                         related_name='salesorder_spec_system', null=True, blank=True)
    aluminium_specification = models.ForeignKey(ProfileMasterType, on_delete=models.PROTECT,
                                       related_name="salesorder_specification", null=True, blank=True)
    
    aluminium_series = models.ForeignKey(Profile_Kit, on_delete=models.PROTECT,
                                       related_name="salesorder_specif_category", null=True, blank=True)
    panel_category = models.ForeignKey(PanelMasterBase, on_delete=models.PROTECT,
                                       related_name='salesorder_panel_material', null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.PROTECT,
                                    related_name='salesorder_panel_barnd', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.PROTECT,
                                     related_name='salesorder_panel_series', null=True, blank=True)
    panel_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                            related_name='salesorder_panel_specification', null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='salesorder_spec_panel_product', null=True, blank=True)
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, null=True, blank=True, related_name='salesorder_specification_surface_finish')
    surface_finish_color = models.ForeignKey(SurfaceFinishColors, on_delete=models.PROTECT, null=True, blank=True, related_name='salesorder_specification_surface_finish_color')
    
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT,  related_name="salesorder_spec_data")
    have_vision_panels = models.BooleanField(default=False)
    have_spandrel_panels = models.BooleanField(default=False)
    have_openable_panels = models.BooleanField(default=False)
    
    vision_panels = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    spandrel_panels = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    openable_panels = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reset_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.identifier
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesOrderSpecification'   
  
    
class SalesSecondarySepcPanels(models.Model):
    PANEL_TYPE = [
        (0, "N/A"),
        (1, "Vision Panel"),
        (2, "Spandrel Panel"),
        (3, "Openable Panel"),
    ]
    
    specifications = models.ForeignKey(SalesOrderSpecification, on_delete=models.PROTECT, related_name='salesorder_sec_spec_panels', null=True, blank=True)
    panel_type = models.IntegerField(choices=PANEL_TYPE, null=True, blank=True)
    panel_category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                       related_name='salesorder_sec_spec_panel_category', null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.PROTECT,
                                    related_name='salesorder_sec_spec_panel_barnd', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.PROTECT,
                                     related_name='salesorder_sec_spec_panel_series', null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='salesorder_sec_spec_panel_product', null=True, blank=True)
    panel_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT, related_name='salesorder_sec_spec_panel_specification', null=True, blank=True)
    
    def __str__(self):
        return self.panel_specification.specifications
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesSecondarySepcPanels'  
        

class SalesOrderItems(models.Model):
    
    TYPE = [
        (1, 'Main Product'),
        (2, 'Associated Product'),
        (3, 'Secondary'),
    ]
    
    
    EPS_UOM = [
        (1, "No's"),
        (2, "Lumpsum"),
        (3, "Linear Meter")
    ]
    
    ref_product = models.ForeignKey(EstimationMainProduct, on_delete=models.PROTECT, null=True, blank=True, related_name='sales_order_ref_pro')
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, default=1, null=True, blank=True)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    specification_Identifier = models.ForeignKey(SalesOrderSpecification, on_delete=models.CASCADE, 
                                                 related_name="salesorder_specification_identifier", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="salesorderitem_category")
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='salesorder_product', null=True, blank=True)
    product_type = models.IntegerField(choices=TYPE, default=1, null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='salesorder_glass_product', null=True, blank=True)
    
    main_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(CategoryBrands, on_delete=models.CASCADE,
                                           related_name='salesorder_item_brand', null=True, blank=True)
    series = models.ForeignKey(Profile_Kit, on_delete=models.CASCADE,
                                           related_name='salesorder_product_series', null=True, blank=True)
    associated_key = models.CharField(max_length=100, null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.CASCADE,
                              related_name='salesorder_product_panel_brand', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.CASCADE,
                               related_name='salesorder_product_panel_series', null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.CASCADE,
                                           related_name='salesorder_product_uom', null=True, blank=True)
    is_sourced = models.BooleanField(default=False, null=True, blank=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                           related_name='salesorder_product_suppliers', null=True, blank=True)
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, 
                                       null=True, blank=True, related_name='salesorder_product_surface_finish')
    
    product_code = models.CharField(max_length=255, null=True, blank=True)
    product_description = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sales_group = models.ForeignKey(SalesOrderGroups, on_delete=models.PROTECT,
                                       related_name="salesorder_group", null=True, blank=True)
    is_accessory = models.BooleanField(default=False)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accessory_quantity = models.IntegerField(null=True, blank=True, default=1)
    accessory_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    enable_addons = models.BooleanField(default=False)
    
    building = models.ForeignKey('projects.EPSBuildingsModel', on_delete=models.PROTECT, related_name="salesorder_building", null=True, blank=True)
    elevation = models.ForeignKey('projects.ElevationModel', on_delete=models.PROTECT, related_name="salesorder_elevation", null=True, blank=True)
    floor = models.ForeignKey('projects.FloorModel', on_delete=models.PROTECT, related_name="salesorder_floor", null=True, blank=True)
    
    eps_uom = models.IntegerField(choices=EPS_UOM, null=True, blank=True)
    
    def get_area(self):
        area = (float(self.width) * float(self.height))/1000000
        total_area = float(area) * float(self.quantity)
        self.area = area 
        self.total_area = total_area
        
    def save(self, *args, **kwargs):
        if self.width and self.height and self.quantity:
            self.get_area()
        else:
            self.area = 1
            self.total_area = float(self.quantity)
            
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesOrderItems'
    
    
    
class SalesOrderInfill(models.Model):
    
    PANEL_TYPE = [
        (1, "Vision Panel"),
        (2, "Spandrel Panel"),
        (3, "Openable Panel"),
    ]
    
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name='sales_item_infill')
    infill_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                           related_name='salesorder_group_infill_specifi', null=True, blank=True)
    infill_area = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    infill_primary = models.BooleanField(default=True, null=True, blank=True)
    
    infill_width = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    infill_height = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    infill_quantity = models.IntegerField(default=1, null=True, blank=True)
    panel_type = models.IntegerField(choices=PANEL_TYPE, null=True, blank=True)
    
    def __str__(self):
        return self.infill_specification.specifications
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesOrderInfill'


class SalesOrderAccessories(models.Model):
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name='sales_item_accessory')
    accessory_item = models.ForeignKey(AccessoriesKitItem, on_delete=models.PROTECT, related_name='sales_item_accessory_kit', null=True, blank=True)
    accessory_item_quantity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    accessory_item_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    accessory_item_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}SalesOrderAccessories'
       
class SalesOrderAddons(models.Model):
    PRICING_TYPE = [
        (1, "Lm"), #Price per Linear Meter
        (2, "SqM"), #Price per Square Meter
        (3, "No's") #Price per Unit
    ]
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name='sales_item_addons')
    addons = models.ForeignKey(Addons, on_delete=models.PROTECT, null=True, blank=True, related_name='sales_order_addons')
    pricing_type = models.IntegerField(choices=PRICING_TYPE, null=True, blank=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    addon_quantity = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
       
class ProjectContractItems(models.Model):
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name='project_contract_item')
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name='+')
    infill_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    authorised_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    auth_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    eps_issued = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    eps_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Contract_Items'
       
        
class ContractItems(models.Model):
    project_contract = models.ForeignKey(ProjectContractItems, on_delete=models.PROTECT, related_name='project_contract')
    associated_product = models.ForeignKey(AssociatedProducts, on_delete=models.PROTECT, blank=True, null=True)
    associated_product_quantity = models.CharField(max_length=50, default=0)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Contract_Items'
       
        
class ProjectInvoicingPercentage(models.Model):
    STAGE = [
        (1, 'Delivery'),
        (2, 'Stage 1'),
        (3, 'Stage 2'),
        (4, 'Stage 3'),
    ]
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="invoice_percentage_project")
    # stage = models.ForeignKey(Invoice_Settings, on_delete=models.PROTECT, related_name="invoice_percentage_stage")
    stage = models.IntegerField(choices=STAGE)
    invoice_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                            MaxValueValidator(100.0)], default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Invoicing_Percentage'
    
    def __str__(self):
        return self.get_stage_display()
  
        
class ProjectDeductionPercentage(models.Model):
    
    STAGE = [
        (1, 'Advance'),
        (2, 'Retention'),
    ]
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="deduction_percentage_project")
    deduction_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                            MaxValueValidator(100.0)], default=0, null=True, blank=True)
    deduction_stage = models.IntegerField(choices=STAGE)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Deduction_Percentage'
    
           
class ProjectInvoices(BaseModel):
    STATUS = [
        (1, 'Uncertified'),
        (2, 'Certified'),
    ]
    TERMS_OF_PAYMENT = [
        (1, 'Immediate'),
        (2, '15 Days'),
        (3, '30 Days'),
        (4, '45 Days'),
        (5, '60 Days'),
    ]
    
    INVOICE_STAGE = [
        (1, 'Work in progress'),
        (2, 'Final'),
    ]
    
    INVOICE_TYPE = [
        (1, 'Normal'),
        (2, 'Cumulative'),
    ]
    
    MODE_OF_PAYMENT = [
        ('', 'Select a Option'),
        (1, 'Credit'),
        (2, 'Cash'),
    ]
    
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="project_invoices")
    invoice_number = models.CharField(max_length=255, blank=True, null=True)
    company = models.ForeignKey(Companies, on_delete=models.PROTECT, related_name="comapny_invoices")
    project_invoice_status = models.IntegerField(choices=STATUS, default=1, null=True, blank=True)
    invoice_value = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    invoice_due_date = models.DateTimeField()
    bill_to_name = models.CharField(max_length=255, null=True, blank=True)
    bill_to_email = models.CharField(max_length=255, null=True, blank=True)
    bill_to_address = models.CharField(max_length=500, null=True, blank=True)
    bill_to = models.ForeignKey(Customers, on_delete=models.PROTECT, null=True, blank=True, related_name="project_invoice_customer")
    invoice_notes = models.CharField(max_length=1000, null=True, blank=True)
    terms_of_payment = models.IntegerField(choices=TERMS_OF_PAYMENT)
    invoice_type = models.IntegerField(choices=INVOICE_TYPE, null=True, blank=True)
    invoice_stage = models.IntegerField(choices=INVOICE_STAGE, default=1, null=True, blank=True)
    mode_of_payment = models.IntegerField(choices=MODE_OF_PAYMENT, null=True, blank=True)
    
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Invoces'
   
        
class ProjectDeliveryQuantity(models.Model):
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    wcr = models.ForeignKey('projects.ProjectWCR', on_delete=models.PROTECT, related_name="wcr_qunatity_delivery")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="project_delivery_qunatity")
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name="delivery_qunatity_product")
    delivered_qunatity = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    delivered_not_invoiced = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Delivery_Quantity'


class ProjectInstalledQuantity(models.Model):
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    wcr = models.ForeignKey('projects.ProjectWCR', on_delete=models.PROTECT, related_name="wcr_qunatity_installation")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="project_installed_qunatity")
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name="installed_qunatity_product")
    installed_qunatity = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    installed_not_invoiced = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Installed_Quantity'
     
                
class ProjectInvoicingProducts(models.Model):
    invoice = models.ForeignKey(ProjectInvoices, on_delete=models.PROTECT, related_name="project_invoice")
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name="project_invoice_product")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="invoice_product_project")
    # invoicing_stage = models.ForeignKey(ProjectInvoicingPercentage, on_delete=models.PROTECT, related_name="project_invoice_percentage")
    invoice_percentage = models.DecimalField(max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    # unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_Invoiced_Products'

class CumulativeInvoiceProduct(models.Model):
    
    invoice = models.ForeignKey(ProjectInvoices, on_delete=models.PROTECT, related_name="project_cumulative_invoice")
    product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, related_name="project_cumulative_invoice_product")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="invoice_cumulative_product_project")
    invoice_percentage = models.DecimalField(max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=8, default=0, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}CumulativeInvoiceProduct'
        
            
class ProjectWCR(BaseModel):
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name="project_wcr")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    wcr_number = models.CharField(max_length=255, blank=True, null=True)
    wcr_notes = models.CharField(max_length=1000, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Project_WCR'
     
        
class WCRProducts(models.Model):
    wcr = models.ForeignKey(ProjectWCR, on_delete=models.PROTECT, related_name="product_wcr")
    wcr_product = models.ForeignKey(SalesOrderItems, on_delete=models.PROTECT, null=True, blank=True, related_name="project_wcr_product")
    delivery_qunatity = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    installed_qunatity = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}WCRProducts'
        
# 
# 
# EPS MODEL
# 
# 

class Eps_main(BaseModel):
    STATUS = [
        (1, "Received"),
        (2, "In Progress"),
        (3, "Completed"),
    ]
    
    PRIORITY = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
    ]
    
    EPS_TYPE = [
        (1, 'Product EPS'),
        (2, 'Infill EPS'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="eps_created_by")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name='eps_project', null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    eps_priority = models.IntegerField(choices=PRIORITY, default=3)
    
    eps_id = models.CharField(max_length=50, null=True, blank=True)
    eps_products = models.ManyToManyField('projects.Eps_Products')
    expec_delivery_date = models.DateTimeField(blank=True, null=True)
    
    # confirmation
    is_understand = models.BooleanField(default=False)
    is_confirm = models.BooleanField(default=False)
    is_agreed = models.BooleanField(default=False)
    eps_note = models.CharField(max_length=500, null=True, blank=True)
    rating = models.IntegerField(default=0)
    eps_type = models.IntegerField(choices=EPS_TYPE, default=1)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EPS_Main'
    
             
class Eps_ShopFloors(models.Model):
    
    shopfloor = models.ForeignKey('shopfloors.Shopfloors', on_delete=models.PROTECT, null=True, blank=True, related_name="eps_associated_shopfloor")
    required_delivery_date = models.DateField(null=True, blank=True)
    shop_floor_notes = models.CharField(max_length=500, null=True, blank=True)
    product = models.ForeignKey('projects.Eps_Products', on_delete=models.PROTECT, related_name='eps_shopfloor_product')
    eps = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='eps_shopfloor_data')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_ShopFloors'
    
        
class ShopFloor_Doc(models.Model):
    shopfloor_doc = models.FileField(upload_to='shopfloor/', validators=[FileExtensionValidator(['pdf', 'csv', 'xlsx'])], blank=True, null=True, max_length=10000)
    eps_product = models.ForeignKey(Eps_ShopFloors, on_delete=models.PROTECT, related_name="eps_shopfloor_attachment", null=True, blank=True)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}ShopFloor_Doc'
    
                   
class Eps_Products(models.Model):
    STATUS = [
        (1, "Received"),
        (2, "Awaiting Materials"),
        (3, "On-Hold"),
        (4, "Scheduled"),
        (5, "In Que"),
    ]
    
    ALUM_STATUS = [
        (1, "Yet to Process"),
        (2, "Awaiting Materials"),
        (3, "In Stock"),
        (4, "Partial Stock"),
        (5, "N/A")
    ]
    
    INFILL_STATUS = [
        (1, "Yet to Process"),
        (2, "OutSource"),
        (3, "Receiving"),
        (4, "Received"),
    ]
    
    ACCESSORY_STATUS = [
        (1, "Yet to Process"),
        (2, "Out of Stock"),
        (3, "In Stock"),
        (4, "Partial Stock"),
        (5, "N/A")
    ]
    
    SHOPFLOOR_STATUS = [
        (1, "Received"),
        (2, "Scheduled"),
        (3, "On-Hold"),
        (4, "Completed"),
        (5, "N/A")
    ]
    
    QAQC_STATUS = [
        (1, "Received"),
        (2, "Completed")
    ]
    
    INSPECTION_STATUS = [
        (1, "Yet to Process"),
        (2, "Partialy Completed"),
        (3, "Completed"),
    ]
    
    
    created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="eps_product_created_by")
    eps_product = models.ForeignKey(ProjectContractItems, on_delete=models.PROTECT, related_name="eps_product_item")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name='eps_product_project')
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eps_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eps_total_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_remaining_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_type = models.CharField(max_length=50, null=True, blank=True)
    eps_product_note = models.CharField(max_length=200 , null=True, blank=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    eps_product_attachment = models.FileField(upload_to='attachments/', validators=[FileExtensionValidator(['pdf', 'csv', 'xlsx'])], max_length=10000, null=True, blank=True)
    eps_product_details = models.ForeignKey('projects.Eps_Product_Details', on_delete=models.PROTECT, related_name='eps_product_details_main', null=True, blank=True)
    product_status = models.IntegerField(choices=STATUS, default=5)
    eps_data = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name="eps_related_to_product", null=True, blank=True)
    
    # no_infill_data = models.BooleanField(default=False)
    
    # fabrication_drawings_req = models.BooleanField(default=False)
    fabrication_drawings_not_req = models.BooleanField(default=False)
    fabrication_note = models.CharField(max_length=1000, null=True, blank=True)
    aluminium_status = models.IntegerField(choices=ALUM_STATUS, default=1)
    infill_status = models.IntegerField(choices=INFILL_STATUS, default=1)
    accessory_status = models.IntegerField(choices=ACCESSORY_STATUS, default=1)
    shopfloor_status = models.IntegerField(choices=SHOPFLOOR_STATUS, default=1)
    qaqc_status = models.IntegerField(choices=QAQC_STATUS, null=True, blank=True)
    inspection_status = models.IntegerField(choices=INSPECTION_STATUS, default=1)
    
    vision_panel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_vision_panel = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    spandrel_panel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_spandrel_panel = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    openable_panel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_openable_panel = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    is_vp = models.BooleanField(default=False)
    is_sp = models.BooleanField(default=False)
    is_op = models.BooleanField(default=False)
    
    
    vp_description = models.CharField(max_length=250, null=True, blank=True)
    op_description = models.CharField(max_length=250, null=True, blank=True)
    sp_description = models.CharField(max_length=250, null=True, blank=True)
    
    
    def calc_area(self):
        if self.width and self.height:
            area = (float(self.width) * float(self.height))/1000000
        else:
            area = 0
            
        self.eps_area = area
        total_area = float(area)*float(self.quantity)
        self.eps_total_area = total_area
        
        # if not self.infill_remaining_area:
        #     self.infill_remaining_area = total_area
    
        
        
    def save(self, *args, **kwargs):
        if self.eps_product.product.eps_uom == 1:
            print("S")
            if self.width and self.height and self.quantity:
                print("W")
                self.calc_area()
            
        else:
            if not self.infill_remaining_area:
                print("R")
                self.infill_remaining_area = self.quantity
                
        super().save(*args, **kwargs)
            
    class Meta:
        db_table = f'{TABLE_PREFIX}EPS_Products'
         
         
class Eps_Product_Details(models.Model):
    
    product_part = models.ForeignKey(Parts, on_delete=models.PROTECT, related_name='eps_product_details', null=True, blank=True)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_length =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_total_length =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_width =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_height =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_area =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_total_area =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    main_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name='eps_product_main', null=True, blank=True)
    add_later = models.BooleanField(default=True)
    product_description = models.CharField(max_length=200, null=True, blank=True)
    
    def calculate_area(self):
        area = (float(self.product_width)*float(self.product_height))/1000000
        self.product_area = area
        total_area = float(area)*float(self.product_quantity)
        self.product_total_area = total_area
        
    def save(self, *args, **kwargs):
        if self.product_width and self.product_height and self.product_quantity:
            self.calculate_area()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EPS_Products_Details'
       

class Temp_EPS_Products(models.Model):
    STATUS = [
        (1, "Not Processed"),
        (2, "Processed"),
    ]
    product = models.ForeignKey(ProjectContractItems, on_delete=models.PROTECT, related_name="eps_temp_created")
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, related_name='eps_temp_product_project')
    product_status = models.IntegerField(choices=STATUS, default=1)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EPS_Products'
    
        
class Eps_Associated_Products(models.Model):
    
    product = models.ForeignKey(Eps_Product_Details, on_delete=models.PROTECT, related_name='eps_associated', null=True, blank=True) 
    eps_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name='eps_product_associated')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Associated_Products'
    
    
class Eps_Associated_sub_Products(models.Model):
    
    main_product = models.ForeignKey(Eps_Product_Details, on_delete=models.PROTECT, related_name='Original_associated_product_eps')
    name = models.CharField(max_length=500)
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Associated_sub_Products'
    
    
class Eps_infill_Details(models.Model):
    
    PANEL_TYPE = [
        (1, "Vision Panel"),
        (2, "Spandrel Panel"),
        (3, "Openable Panel"),
    ]
    
    CHOICES = [
        (1, "Yet to Process"),
        (2, "Partially Outsourced"),
        (3, "OutSourced"),
        # (3, "Receiving"),
        # (4, "Received"),
    ]
    
    RECV_STATUS = [
        (1, "Yet to Receive"),
        (2, "Partially Received"),
        (3, "Received"),
    ]
    
    # infill = models.ForeignKey(SalesOrderInfill, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_infill')
    infill = models.ForeignKey(SalesSecondarySepcPanels, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_infill')
    infill_code = models.CharField(max_length=50, null=True, blank=True)
    infill_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    main_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name='eps_infill_main', null=True, blank=True)
    infill_total_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_outsourced = models.BooleanField(default=False)
    form_infill_eps = models.BooleanField(default=False)
    eps_ref = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='eps_infill_main_ref', null=True, blank=True)
    panel_type = models.IntegerField(choices=PANEL_TYPE, null=True, blank=True)
    status = models.IntegerField(choices=CHOICES, default=1)
    recv_status = models.IntegerField(choices=RECV_STATUS, default=1)
    
    def calc_area(self):
        self.infill_total_area = float(self.infill_area)*float(self.infill_quantity)
    
    def save(self, *args, **kwargs):
        self.calc_area()
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = f'{TABLE_PREFIX}EPS_Infill_Details'


class Eps_infill_Temp(models.Model):
    PANEL_TYPE = [
        (1, "Vision Panel"),
        (2, "Spandrel Panel"),
        (3, "Openable Panel"),
    ]
    # infill = models.ForeignKey(SalesOrderInfill, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_infill_temp')
    infill = models.ForeignKey(SalesSecondarySepcPanels, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_infill_temp')
    infill_code = models.CharField(max_length=50, null=True, blank=True)
    infill_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    infill_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    main_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name='eps_infill_main_temp', null=True, blank=True)
    form_infill_eps = models.BooleanField(default=True)
    eps_ref = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='temp_eps_infill_main_ref', null=True, blank=True)
    # is_outsourced = models.BooleanField(default=False)
    panel_type = models.IntegerField(choices=PANEL_TYPE, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EPS_Infill_Temp'
      
              
class Fabrication_Attachments(models.Model):
    fabrication_docs = models.FileField(upload_to='fabrications/', validators=[FileExtensionValidator(['pdf', 'csv', 'xlsx'])], max_length=10000, blank=True, null=True)
    eps_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name="eps_product_fabrication", null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Fabrication_attachments'
    
        
class Eps_Outsource_items(models.Model):
    
    infill_product = models.ForeignKey(Eps_infill_Details, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_production_items')
    
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    actual_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    out_source_batch = models.ForeignKey('projects.Eps_Outsourced_Data', on_delete=models.PROTECT, null=True, blank=True, related_name='eps_out_source_batch')
    outsource_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Outsource_items'
   
               
class Eps_Outsourced_Data(models.Model):
    
    outsource_date = models.DateTimeField()
    batch_number = models.CharField(max_length=255, null=True, blank=True)
    outsource_number = models.CharField(max_length=255, null=True, blank=True)
    outsource_supplier = models.ForeignKey(Suppliers, on_delete=models.PROTECT, related_name='outsource_suppliers')
    products = models.ManyToManyField(Eps_Outsource_items)
    expected_dalivery_date = models.DateTimeField()
    eps = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='outsource_eps')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Outsourced_Data' 
       
        
class Outsource_receive_recode(models.Model):
    
    receive_date = models.DateTimeField()
    OS_delivery_number = models.CharField(max_length=255)
    received_items = models.ManyToManyField(Eps_Outsource_items)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Outsource_receive_recode'
    
class Outsource_receive_items(models.Model):
    receive_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    item = models.ForeignKey(Eps_Outsource_items, on_delete=models.PROTECT, related_name='outsource_recived_products')
    received_batch = models.ForeignKey(Outsource_receive_recode, null=True, blank=True, on_delete=models.PROTECT, related_name='outsource_recived_batch')
    received_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Outsource_receive_items'
    
class Eps_ShopFloor_main_products(models.Model):
    
    SHOPFLOOR_STATUS = [
        (1, "Ongoing"),
        (2, "Onhold"),
        (3, "Completed")
    ]
    
    main_products = models.ForeignKey(Eps_Product_Details, on_delete=models.PROTECT, related_name='eps_shopfloor_main_product')
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.IntegerField(choices=SHOPFLOOR_STATUS, default=1) 
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_ShopFloor_main_products'
    
    
class Eps_ShopFloor_associated_products(models.Model):
    
    SHOPFLOOR_STATUS = [
        (1, "Ongoing"),
        (2, "Onhold"),
        (3, "Completed")
    ]
    
    main_products = models.ForeignKey(Eps_Associated_sub_Products, on_delete=models.PROTECT, related_name='eps_shopfloor_associated_main_product')
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.IntegerField(choices=SHOPFLOOR_STATUS, default=1) 
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_ShopFloor_associated_products'
    
    
class Schedule_Product(models.Model):
    SHOPFLOOR_STATUS = [
        (1, "Received"),
        (2, "Scheduled"),
        (3, "On-Hold"),
        (4, "Completed"),
    ]
    
    PROCESSING_TYPE = [
        (1, "In-House"),
        (2, "Outsource"),
    ]
    product = models.ForeignKey(Eps_ShopFloor_main_products, on_delete=models.PROTECT, related_name='scheduled_product')
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    eps = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='eps_scheduld_products')
    shopfloor_status = models.IntegerField(choices=SHOPFLOOR_STATUS, default=1)
    processing_type = models.IntegerField(choices=PROCESSING_TYPE)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    in_workstation = models.BooleanField(default=False)
    
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Schedule_Product'
   
class InfillSchedule(models.Model):
    
    product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name='infill_scheduled_product')
    start_date = models.DateField(default=django.utils.timezone.now)
    eps = models.ForeignKey(Eps_main, on_delete=models.PROTECT, null=True, blank=True, related_name='eps_infill_scheduld_products')
    
    # expected_completion = models.DateField(null=True, blank=True)
    # notes = models.CharField(max_length=1000, null=True, blank=True)
    # required_delivery_date = models.DateField(null=True, blank=True)
    
    
    class Meta:
        db_table = f'{TABLE_PREFIX}InfillSchedule'
    
    
class Workstation_Data(BaseModel):
    
    LABEL = [
        (0, "Select"),
        (1, "Accepted"),
        (2, "Rejected"),
    ]
    
    QAQC_STATUS = [
        (1, "Accepted"),
        (2, "Rejected"),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_productworkstation')
    product = models.ForeignKey(Eps_ShopFloor_main_products, on_delete=models.PROTECT, related_name='product_productworkstation')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    workstation = models.ForeignKey(Workstations, on_delete=models.PROTECT, related_name='productworkstation')
    is_completed = models.BooleanField(default=False)
    eps_product_id = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name="eps_product_workstation")
    
    qaqc_received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    qaqc_remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    qaqc_completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_qaqc_completed = models.BooleanField(default=False)
    qaqc_status = models.IntegerField(choices=QAQC_STATUS, null=True, blank=True)
    
    delivery_remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    delivery_completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    prev_product = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name="previous_workstation_product_id")
    total_completion_time = models.TextField(null=True, blank=True, default='00:00')
    rating = models.IntegerField(default=0)
    
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Workstation_Data'
    
        
class Workstation_Associated_Products_Data(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_associated_productworkstation')
    product = models.ForeignKey(Eps_Associated_sub_Products, on_delete=models.PROTECT, related_name='product_associated_productworkstation')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    workstation = models.ForeignKey(Workstations, on_delete=models.PROTECT, related_name='associated_productworkstation')
    is_completed = models.BooleanField(default=False)
    eps_product_id = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, related_name="eps_associated_product_workstation")
    
    qaqc_received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    qaqc_remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    qaqc_completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_qaqc_completed = models.BooleanField(default=False)
    
    delivery_remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    delivery_completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    prev_product = models.ForeignKey('self', on_delete=models.PROTECT,  null=True, blank=True, related_name="previous_workstation_product_id_associated")
    total_completion_time = models.TextField(null=True, blank=True, default='00:00')
    rating = models.IntegerField(default=0)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Workstation_Associated_Products_Data'
    
    
class Workstation_History(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_productworkstation_history')
    date = models.DateTimeField(default=django.utils.timezone.now)
    workstation_data = models.ForeignKey(Workstation_Data, on_delete=models.PROTECT, related_name='productworkstation_history_main')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completion_time = models.CharField(max_length=10, default='00:00')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Workstation_History'
     
        
class Workstation_Associated_Product_History(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_associatedproductworkstation_history')
    date = models.DateTimeField(default=django.utils.timezone.now)
    workstation_data = models.ForeignKey(Workstation_Associated_Products_Data, on_delete=models.PROTECT, related_name='associated_productworkstation_history_main')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completion_time = models.CharField(max_length=10, default="00:00")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Workstation_Associated_Product_History'
     
        
class Eps_QAQC(BaseModel):
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_eps_qaqc')
    product = models.ForeignKey(Schedule_Product, on_delete=models.PROTECT, null=True, blank=True, related_name="qaqc_product")
    panel_product = models.ForeignKey(Eps_Products, on_delete=models.PROTECT, null=True, blank=True, related_name="qaqc_panel_product")
    pss = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_QAQC'  
      

class QAQC_infill_Products(models.Model):
    product = models.ForeignKey(Eps_Outsource_items, on_delete=models.PROTECT, related_name='qaqc_infill_product')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_qaqc_completed = models.BooleanField(default=False)
    
    delivery_remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    delivery_completed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_infill_Products'
      
            
class QAQC_Main_Product_History(models.Model):
    LABEL = [
        (0, "Select"),
        (1, "Accepted"),
        (2, "Rejected"),
    ]
    
    product = models.ForeignKey("projects.Workstation_Data", on_delete=models.PROTECT, related_name="qaqc_mainproduct_history")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="qaqc_mainproduct_history_created_by")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    date = models.DateTimeField(default=django.utils.timezone.now)
    # specification = models.IntegerField(choices=LABEL, default=0)
    # appearance = models.IntegerField(choices=LABEL, default=0)
    # functional = models.IntegerField(choices=LABEL, default=0)
    # labeling = models.IntegerField(choices=LABEL, default=0)
    # joiners = models.IntegerField(choices=LABEL, default=0)
    rating = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_Main_Product_History'
       
        
class QAQC_Associated_Product_History(models.Model):
    LABEL = [
        (0, "Select"),
        (1, "Accepted"),
        (2, "Rejected"),
    ]
    
    product = models.ForeignKey("projects.Workstation_Associated_Products_Data", on_delete=models.PROTECT, related_name="qaqc_associatedproduct_history")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="qaqc_associatedproduct_history_created_by")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    date = models.DateTimeField(default=django.utils.timezone.now)
    
    # specification = models.IntegerField(choices=LABEL, default=0)
    # appearance = models.IntegerField(choices=LABEL, default=0)
    # functional = models.IntegerField(choices=LABEL, default=0)
    # labeling = models.IntegerField(choices=LABEL, default=0)
    # joiners = models.IntegerField(choices=LABEL, default=0)
    rating = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_Associated_Product_History'
       
          
class QAQC_Infill_History(models.Model):
    LABEL = [
        (0, "Select"),
        (1, "Accepted"),
        (2, "Rejected"),
    ]
    
    product = models.ForeignKey("projects.QAQC_infill_Products", on_delete=models.PROTECT, related_name="qaqc_infillproduct_history")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="qaqc_infillproduct_history_created_by")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    date = models.DateTimeField(default=django.utils.timezone.now)
    # specification = models.IntegerField(choices=LABEL, default=0)
    # appearance = models.IntegerField(choices=LABEL, default=0)
    # functional = models.IntegerField(choices=LABEL, default=0)
    # labeling = models.IntegerField(choices=LABEL, default=0)
    # joiners = models.IntegerField(choices=LABEL, default=0)
    rating =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_Infill_History'     
        
        
class Eps_Products_For_Delivery(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_delivery_products')
    product = models.ForeignKey(Schedule_Product, on_delete=models.PROTECT, null=True, blank=True, related_name="product_for_delivery")
    outsourced_product = models.ForeignKey(QAQC_infill_Products, on_delete=models.PROTECT, null=True, blank=True, related_name='outsourced_product_in_delivery')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Products_For_Delivery'
    
        
class Delivery_Product_Cart_Main(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_delivery_products_cart_main')
    product = models.ForeignKey(Workstation_Data, on_delete=models.PROTECT, related_name="product_for_delivery_cart_main")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Delivery_Product_Cart_Main'
      
        
class Delivery_Product_Cart_Associated(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_delivery_products_cart_associated')
    product = models.ForeignKey(Workstation_Associated_Products_Data, on_delete=models.PROTECT, related_name="product_for_delivery_cart_associated")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Delivery_Product_Cart_Associated'
        
        
class Delivery_Product_Cart_infill(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_delivery_products_cart_infill')
    product = models.ForeignKey(QAQC_infill_Products, on_delete=models.PROTECT, related_name="product_for_delivery_cart_infill")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Eps_Delivery_Product_Cart_infill'
        
        
class Delivery_Note(BaseModel):
    STATUS = [
        (1, "Pending Schedule"),
        (2, "Delivery Scheduled"),
        # (3, "Shipment"),
        (3, "Delivered"),
        (4, "Returned"),
        
    ]
    
    INSPECTION_STATUS = [
        (1, "Yet to Process"),
        (2, "Partialy Completed"),
        (3, "Completed"),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_by_delivery_note')
    delivery_date = models.DateTimeField()
    eps = models.ForeignKey(Eps_main, on_delete=models.PROTECT, related_name='delivery_note_eps')
    driver = models.ForeignKey(Drivers, on_delete=models.PROTECT, null=True, blank=True, related_name='delivery_driver')
    vehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT, null=True, blank=True, related_name='delivery_vehicle')
    delivery_notes = models.CharField(max_length=1000, null=True, blank=True)
    main_product = models.ManyToManyField(Workstation_Data)
    associated_product = models.ManyToManyField(Workstation_Associated_Products_Data)
    infill_product = models.ManyToManyField(QAQC_infill_Products)
    delivery_note_id = models.CharField(max_length=225)
    status = models.IntegerField(choices=STATUS, default=1)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inspect_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inspection_status = models.IntegerField(choices=INSPECTION_STATUS, default=1)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Delivery_Notes'  
       
       
  
class DeliveryNoteCart(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='dn_cart_createdby')
    temp_dn = models.ForeignKey(Delivery_Note, on_delete=models.PROTECT, related_name='cart_dn')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}DeliveryNoteCart'
    
    
class Inspection_History(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inspection_history_createdby')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dn_details = models.ForeignKey(Delivery_Note, on_delete=models.PROTECT, related_name='inspection_history_dn')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Inspection_History'
        
        
class EPSBuildingsModel(models.Model):
    building_name = models.CharField(max_length=225)
    project = models.ForeignKey(ProjectsModel, on_delete=models.PROTECT, null=True, blank=True, related_name='building_eps_project')
    
    def __str__(self):
        return self.building_name
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EPSBuildingsModel'
    
        
class ElevationModel(models.Model):
    elevation = models.CharField(max_length=225)
    building = models.ForeignKey(EPSBuildingsModel, on_delete=models.PROTECT, null=True, blank=True, related_name='building_evevation')
    
    def __str__(self):
        return self.elevation
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ElevationModel'
        

class FloorModel(models.Model):
    floor_name = models.CharField(max_length=225)
    elevation = models.ForeignKey(ElevationModel, on_delete=models.PROTECT, null=True, blank=True, related_name='elevation_floor')
    
    def __str__(self):
        return self.floor_name
    
    class Meta:
        db_table = f'{TABLE_PREFIX}FloorModel'

    
class ProjectApprovalTypes(models.Model):
    approval_type = models.CharField(max_length=225)
    
    def __str__(self):
        return f'{self.approval_type}'
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProjectApprovalTypes'
        

class ProjectApprovalStatus(models.Model):
    approval_status = models.CharField(max_length=225)
    color = models.CharField(max_length=225)
    
    def __str__(self):
        return f'{self.approval_status}'
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProjectApprovalStatus'
        
class ProjectSepcificationsApproval(models.Model):
    specification = models.ForeignKey(SalesOrderSpecification, on_delete=models.PROTECT, null=True, blank=True, related_name='project_approved_spec')
    approve_type = models.ForeignKey(ProjectApprovalTypes, on_delete=models.PROTECT, null=True, blank=True, related_name='project_approved_type')
    status = models.ForeignKey(ProjectApprovalStatus, on_delete=models.PROTECT, null=True, blank=True, related_name='project_approved_type_status')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProjectSepcificationsApproval'

class ApprovalNotes(models.Model):
    specification = models.ForeignKey(SalesOrderSpecification, on_delete=models.PROTECT, null=True, blank=True, related_name='project_approved_spec_notes')
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='approval_notes_user')
    notes = models.CharField(max_length=500, null=True, blank=True)
    date_time = models.DateTimeField(default=django.utils.timezone.now)
    modified_time = models.DateTimeField(null=True, blank=True,)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ApprovalNotes'
    

class ApprovalSpecFiles(models.Model):
    specification = models.ForeignKey(SalesOrderSpecification, on_delete=models.PROTECT, null=True, blank=True, related_name='project_approved_spec_files')
    approval_file = models.FileField(upload_to='eps_specification/files', null=True, blank=True)
    approval_name = models.CharField(max_length=250, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ApprovalSpecFiles'
        
        
class QAQC_parameters(models.Model):
    parameter_name = models.CharField(max_length=225)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_parameters'

    
class QAQC_RatingHistory(models.Model):
    product_item = models.ForeignKey(Eps_Product_Details, on_delete=models.PROTECT, null=True, blank=True, related_name='qaqc_product_process_item')
    rate = models.IntegerField(null=True, blank=True)
    qaqc_process_data = models.ForeignKey(QAQC_Main_Product_History, on_delete=models.PROTECT, null=True, blank=True, related_name='qaqc_product_history')
    qaqc_associated_process_data = models.ForeignKey(QAQC_Associated_Product_History, on_delete=models.PROTECT, null=True, blank=True, related_name='qaqc_associated_product_history')
    qaqc_process_infill_data = models.ForeignKey(QAQC_Infill_History, on_delete=models.PROTECT, null=True, blank=True, related_name='qaqc_product_infill_history')
    infill_product_item = models.ForeignKey(QAQC_infill_Products, on_delete=models.PROTECT, null=True, blank=True, related_name='qaqc_product_process_item_infill')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}QAQC_RatingHistory'
    