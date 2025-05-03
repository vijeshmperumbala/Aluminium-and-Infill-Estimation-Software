import datetime
from datetime import timedelta
import django
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.brands.models import CategoryBrands
from apps.companies.models import Companies
# from apps.estimations.models import EstimationMainProduct, MainProductGlass
from apps.panels_and_others.models import (
        PanelMasterBase, 
        PanelMasterBrands,
        PanelMasterConfiguration, 
        PanelMasterSeries,
        PanelMasterSpecifications
)
from apps.pricing_master.models import (
        AdditionalandLabourPriceMaster, 
        PriceMaster, 
        SealantPriceMaster, 
        Surface_finish_Master, 
        Surface_finish_kit,
)
from apps.product_parts.models import Profile_Kit
from apps.profiles.models import ProfileMasterType
from apps.industry_type.models import IndustryTypeModal
from apps.product_master.models import Product
from apps.user.models import BaseModel, User
from apps.Categories.models import Category
from apps.customers.models import Customers

from amoeba.settings import TABLE_PREFIX


class Enquiries(BaseModel):
    TYPE = [
        (1, 'Client'),
        (2, 'In House'),
    ]
    
    STATUS = [
       (1, 'Created'), # Created
       (2, 'Estimating'),
    #    (3, 'Submitted'),
       (4, 'Inactive'),
       (5, 'Management Approved'),
       (6, 'Lose'),
       (7, 'Enquiry On Hold'),
       (8, 'Awarded'),
       (9, 'Management Review'),
       (10, 'Quotation Sent'),
       (0, 'Test'),
    ]
    
    PRICING_TYPE = [
        (1, 'International'),
        (2, 'Local')
    ]
    
    ENQUIRY_TYPE = [
        (1, 'Ongoing'),
        (2, 'Tender'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_enquiry")
    title = models.CharField(max_length=255, null=True, blank=True)
    enquiry_category = models.IntegerField(choices=TYPE, null=True, blank=True)
    enquiry_id = models.CharField(max_length=25, null=True, blank=True)
    customers = models.ManyToManyField(Customers, symmetrical=False)
    main_customer = models.ForeignKey(Customers, on_delete=models.PROTECT, related_name="enquiry_main_customer", null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    notifications = models.BooleanField(default=False)
    users = models.ForeignKey(User, on_delete=models.PROTECT, related_name="enquiry_users", null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1, null=True)
    labour_percentage = models.FloatField(validators=[MinValueValidator(0.00)],
                                                    null=True, blank=True, default=0)
    overhead_percentage = models.FloatField(validators=[MinValueValidator(0.00)],
                                                      null=True, blank=True, default=0)
    additional_and_labour = models.ForeignKey(AdditionalandLabourPriceMaster, on_delete=models.PROTECT, related_name="additional_and_labour_enquiry", null=True, blank=True)
    pricing = models.ForeignKey(PriceMaster, on_delete=models.CASCADE, null=True, blank=True)
    pricing_type_select = models.IntegerField(choices=PRICING_TYPE, null=True, blank=True)
    
    price_per_kg = models.CharField(max_length=10, null=True, blank=True)
    price_per_kg_markup = models.FloatField(validators=[MinValueValidator(0.0)], default=0, null=True, blank=True)
    
    enquiry_active_status = models.BooleanField(default=True, null=True, blank=True)
    sealant_pricing = models.ForeignKey(SealantPriceMaster, on_delete=models.CASCADE, null=True, blank=True)
    structural_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weather_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    enquiry_type = models.IntegerField(choices=ENQUIRY_TYPE, null=True, blank=True)
    industry_type = models.ForeignKey(IndustryTypeModal, on_delete=models.PROTECT, related_name="enquiry_industry_type1")
    company = models.ForeignKey(Companies, on_delete=models.PROTECT, related_name='enquiry_company')

    enquiry_members = models.ManyToManyField(User, related_name='enquiry_members')
    surface_finish_price = models.ForeignKey(Surface_finish_Master, on_delete=models.PROTECT, null=True, blank=True, related_name='enquiey_surface_finish_price')
    rating = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    active_hrs = models.DurationField(default=timedelta(0))
    
    other_notes = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Enquiries'

    def __str__(self):
        return self.title

    def get_days_remaining_and_delay(self):
        now = datetime.datetime.now()
        due_date = self.due_date
        received_date = self.received_date
        remaining_days = (due_date - now.date()).days
        delay_days = (now.date() - due_date).days 
        delay_days = max(delay_days, 0)
        
        if remaining_days > 0:
            return {'flag': "Remaining", 'days': remaining_days}
        elif remaining_days == 0:
            return {'flag': "Today", 'days': 0}
        else:
            return {'flag': "Delay", 'days': delay_days}
    
 
class EnquiryUser(models.Model):
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
    enquiry = models.ForeignKey(Enquiries, on_delete=models.CASCADE, related_name="enquiry_active_time")
    active_time = models.DurationField(default=timedelta(0))
    updated_at = models.DateTimeField(null=True, blank=True)
    last_update = models.CharField(max_length=8, default='00:00:00')
    date = models.DateField(default=django.utils.timezone.now)
    status = models.IntegerField(choices=STATUS, null=True, blank=True)
    
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EnquiryUsers' 


@receiver(post_save, sender=EnquiryUser)
def update_enquiry_active_hrs(sender, instance, **kwargs):
    total_active_time = instance.enquiry.enquiry_active_time.aggregate(total_active_time=models.Sum('active_time'))['total_active_time']
    instance.enquiry.active_hrs = total_active_time
    instance.enquiry.save()
    
    
class Estimations(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation_tab")
    enquiry = models.ForeignKey(Enquiries, on_delete=models.CASCADE, related_name='estimation_enquiry', null=True, blank=True)
    version = models.ForeignKey('estimations.EstimationVersions', on_delete=models.CASCADE, related_name='estimation_version', null=True, blank=True)
    inherited_version = models.ForeignKey('estimations.EstimationManiVersion', on_delete=models.CASCADE, related_name='estimation_inherited_version', null=True, blank=True)
    inherited_revision = models.ForeignKey('estimations.EstimationVersions', on_delete=models.CASCADE, related_name='estimation_inherited_revision', null=True, blank=True)
    rating = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Estimations'


class Temp_Estimations(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation_tab_temp")
    enquiry = models.ForeignKey(Enquiries, on_delete=models.CASCADE, related_name='estimation_enquiry_temp', null=True, blank=True)
    version = models.ForeignKey('estimations.EstimationVersions', on_delete=models.CASCADE, related_name='estimation_version_temp', null=True, blank=True)
    inherited_version = models.ForeignKey('estimations.EstimationManiVersion', on_delete=models.CASCADE, related_name='estimation_inherited_version_temp', null=True, blank=True)
    inherited_revision = models.ForeignKey('estimations.EstimationVersions', on_delete=models.CASCADE, related_name='estimation_inherited_revision_temp', null=True, blank=True)
    parent_estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name='parent_estimation_on_temp')
    rating = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Estimations'


class EstimationNotes(BaseModel):
    STATUS = [
        (1, 'Yet to Start'),
        (2, 'Active'),
        (3, 'Submitted'),
        (4, 'Re-Estimating'),
        (5, 'Quotation On Hold'),
        (6, 'Managment Approved'),
        (7, 'Discontinued'),
        (8, 'Reopened'),
        (9, 'Estimating'),
        (10, 'Quote'),
        # (11, 'Drop'),
        (12, 'Quotation Sent'),
        (13, 'Recalled'),
        (14, 'Customer Approved'),
        (15, 'Approved with Signature'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation_notes")
    estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name='note_estimation', null=True, blank=True)
    enquiry = models.ForeignKey(Enquiries, on_delete=models.CASCADE, related_name='note_enquiry', null=True, blank=True)
    management = models.BooleanField(default=False, null=True, blank=True)
    user = models.BooleanField(default=False, null=True, blank=True)
    notes = models.CharField(max_length=2000, null=True, blank=True)
    note_status = models.IntegerField(choices=STATUS, null=True, blank=True)
    is_replay = models.BooleanField(default=False, null=True, blank=True)
    main_note = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='parent_replay')
    note_readed = models.BooleanField(default=False, null=True, blank=True)
    read_by = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True, blank=True, related_name="estimation_note_read_by")
    # tag = models.ForeignKey('tags.Tags', on_delete=models.PROTECT, null=True, blank=True, related_name='note_tag')

    class Meta:
        db_table = f'{TABLE_PREFIX}Estimation_Notes'

    def save(self, *args, **kwargs):
        if self.estimation and not self.enquiry:
            enquiry = Enquiries.objects.get(pk=self.estimation.enquiry.id)
            self.enquiry = enquiry
        super(EstimationNotes, self).save(*args, **kwargs)


class Temp_EstimationNotes(BaseModel):
    STATUS = [
        (1, 'Yet to Start'),
        (2, 'Active'),
        (3, 'Submitted'),
        (4, 'Re-Estimating'),
        (5, 'On Hold'),
        (6, 'Managment Approved'),
        (7, 'Discontinued'),
        (8, 'Reopened'),
        (9, 'Estimating'),
        (10, 'Quote'),
        # (11, 'Drop'),
        (12, 'Quotation Sent'),
        (13, 'Recalled'),
        (14, 'Customer Approved'),
        (15, 'Approved with Signature'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_estimation_notes_temp")
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.CASCADE, related_name='note_estimation_temp', null=True, blank=True)
    enquiry = models.ForeignKey(Enquiries, on_delete=models.CASCADE, related_name='note_enquiry_temp', null=True, blank=True)
    management = models.BooleanField(default=False, null=True, blank=True)
    user = models.BooleanField(default=False, null=True, blank=True)
    notes = models.CharField(max_length=2000, null=True, blank=True)
    note_status = models.IntegerField(choices=STATUS, null=True, blank=True)
    is_replay = models.BooleanField(default=False, null=True, blank=True)
    main_note = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='temp_parent_replay')
    note_readed = models.BooleanField(default=False, null=True, blank=True)
    read_by = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True, blank=True, related_name="estimation_note_read_by_temp")
    # tag = models.ForeignKey('tags.Tags', on_delete=models.PROTECT, null=True, blank=True, related_name='temp_note_tag')

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Estimation_Notes'

    def save(self, *args, **kwargs):
        if self.estimation and not self.enquiry:
            enquiry = Enquiries.objects.get(pk=self.estimation.enquiry.id)
            self.enquiry = enquiry
        super(Temp_EstimationNotes, self).save(*args, **kwargs)
        

class EnquirySpecifications(BaseModel):
    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]
    estimation = models.ForeignKey(Estimations, on_delete=models.PROTECT, related_name='estimation_spe_specification', null=True, blank=True)
    identifier = models.CharField(max_length=50, null=True, blank=True)
    categories = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="enquiry_specif_category")
    aluminium_products = models.ForeignKey(Product, on_delete=models.PROTECT,
                                           related_name='enq_spec_system', null=True, blank=True)
    aluminium_system = models.ForeignKey(CategoryBrands, on_delete=models.PROTECT,
                                         related_name='enq_spec_system', null=True, blank=True)
    aluminium_specification = models.ForeignKey(ProfileMasterType, on_delete=models.PROTECT,
                                       related_name="enquiry_specification", null=True, blank=True)
    aluminium_series = models.ForeignKey(Profile_Kit, on_delete=models.PROTECT,
                                       related_name="enquiry_specif_category", null=True, blank=True)
    panel_category = models.ForeignKey(PanelMasterBase, on_delete=models.PROTECT,
                                       related_name='enqui_panel_material', null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.PROTECT,
                                    related_name='enqui_panel_barnd', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.PROTECT,
                                     related_name='enqui_panel_series', null=True, blank=True)
    panel_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                            related_name='enqui_panel_specification', null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='enq_spec_panel_product', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="created_by_enq_specification")
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, null=True, blank=True, related_name='enquiry_specification_surface_finish')
    is_description = models.BooleanField(default=False)
    specification_description = models.CharField(max_length=225, null=True, blank=True)
    specification_type = models.IntegerField(choices=SPEC_TYPE, default=1)
    minimum_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}EnquirySpecifications'



    def __str__(self):
        return self.identifier
    
    def mini_price_setup(self):
        panel = 0
        product_min_price = 0
        if self.aluminium_products:
            product_min_price = self.aluminium_products.min_price or 0
        
        if self.panel_specification:
            panel_mini_price = PanelMasterConfiguration.objects.filter(panel_specification=self.panel_specification).last()
            panel = panel_mini_price.min_price or 0
        min_price = float(product_min_price)+float(panel)
        self.minimum_price = min_price
    
    # def change_in_infill(self):
    #     spec_products_objs = EstimationMainProduct.objects.filter(specification_Identifier=self.id, panel_product=self.panel_product)
    #     for product in spec_products_objs:
    #         infill_product_objs = MainProductGlass.objects.filter(estimation_product=product)
    #         for infill_product_obj in infill_product_objs:
                
        
    def save(self, *args, **kwargs):
        self.mini_price_setup()
        super().save() 
        

class Temp_EnquirySpecifications(BaseModel):

    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]

    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.PROTECT, related_name='estimation_spe_specification_temp', null=True, blank=True)
    identifier = models.CharField(max_length=50, null=True, blank=True)
    categories = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="enquiry_specif_category_temp")
    aluminium_products = models.ForeignKey(Product, on_delete=models.PROTECT,
                                           related_name='enq_spec_system_temp', null=True, blank=True)
    aluminium_system = models.ForeignKey(CategoryBrands, on_delete=models.PROTECT,
                                         related_name='enq_spec_system_temp', null=True, blank=True)
    aluminium_specification = models.ForeignKey(ProfileMasterType, on_delete=models.PROTECT,
                                       related_name="enquiry_specification_temp", null=True, blank=True)
    aluminium_series = models.ForeignKey(Profile_Kit, on_delete=models.PROTECT,
                                       related_name="enquiry_specif_category_temp", null=True, blank=True)
    panel_category = models.ForeignKey(PanelMasterBase, on_delete=models.PROTECT,
                                       related_name='enqui_panel_material_temp', null=True, blank=True)
    panel_brand = models.ForeignKey(PanelMasterBrands, on_delete=models.PROTECT,
                                    related_name='enqui_panel_barnd_temp', null=True, blank=True)
    panel_series = models.ForeignKey(PanelMasterSeries, on_delete=models.PROTECT,
                                     related_name='enqui_panel_series_temp', null=True, blank=True)
    panel_specification = models.ForeignKey(PanelMasterSpecifications, on_delete=models.PROTECT,
                                            related_name='enqui_panel_specification_temp', null=True, blank=True)
    panel_product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='enq_spec_panel_product_temp', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_enq_specification_temp")
    surface_finish = models.ForeignKey(Surface_finish_kit, on_delete=models.PROTECT, null=True, blank=True, related_name='enquiry_specification_surface_finish_temp')
    is_description = models.BooleanField(default=False)
    specification_description = models.CharField(max_length=225, null=True, blank=True)
    specification_type = models.IntegerField(choices=SPEC_TYPE, default=1)
    minimum_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)


    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_EnquirySpecifications'

    def __str__(self):
        return self.identifier
    
    def save(self, *args, **kwargs):
        panel = 0
        product_min_price = 0
        if self.aluminium_products:
            product_min_price = self.aluminium_products.min_price or 0
        
        if self.panel_specification:
            panel_mini_price = PanelMasterConfiguration.objects.filter(panel_specification=self.panel_specification).last()
            panel = panel_mini_price.min_price or 0
        min_price = float(product_min_price)+float(panel)
        
        self.minimum_price = min_price
        super().save()
    

class Enquiry_Discontinued_History(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="enquiry_discontinued_user")
    discontinue_note = models.CharField(max_length=225, null=True, blank=True)
    enquiry = models.ForeignKey(Enquiries, null=True, blank=True, on_delete=models.CASCADE, related_name="enquiry_discontinued_user")

    class Meta:
        db_table = f'{TABLE_PREFIX}Enquiry_Discontinued_History'


class Enquiry_Log(BaseModel):
    ACTIONS = [
        (1, "Create"),
        (2, "Update"),
        (3, "Delete"),
        (4, "Export"),
        (5, "Download")
    ]
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="enquiry_log_user")
    message = models.CharField(max_length=225, null=True, blank=True)
    enquiry = models.ForeignKey(Enquiries, null=True, blank=True, on_delete=models.CASCADE, related_name="enquiry_log")
    action = models.IntegerField(choices=ACTIONS, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Enquiry_Log'


class Pricing_Summary(models.Model):
    estimation = models.ForeignKey(Estimations, on_delete=models.CASCADE, related_name='pricing_summary_estimation')
    scope_of_work = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    weightage_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    material_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    pricing_review_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    quotation = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Pricing_Summary'


class Temp_Pricing_Summary(models.Model):
    estimation = models.ForeignKey(Temp_Estimations, on_delete=models.CASCADE, related_name='temp_pricing_summary_estimation')
    scope_of_work = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    product_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    weightage_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    material_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    pricing_review_summary = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)
    quotation = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Temp_Pricing_Summary'
        
