import django
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.sealant_types.models import Sealant_Types
from apps.surface_finish.models import Surface_finish

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class PriceMaster(BaseModel):

    TYPE = [
        (1, 'International'),
        (2, 'Local'),
    ]

    STATUS = [
        (1, 'Active'),
        (2, 'Inactive'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_price_master",
                                   null=True, blank=True)
    type = models.IntegerField(choices=TYPE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price_per_kg = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    status = models.IntegerField(choices=STATUS)
    date = models.DateTimeField(null=True, blank=True)
    markup = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)], default=0, null=True, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}PriceMaster'


class AdditionalandLabourPriceMaster(BaseModel):

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_additional_price_master",
                                   null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    ideal_overhead = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])
    ideal_labour = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])
    minimum_overhead = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])
    minimum_labour = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])

    class Meta:
        db_table = f'{TABLE_PREFIX}AdditionalandLabourPriceMaster'
        
    def __str__(self):
        return self.name
    

class SealantPriceMaster(BaseModel):
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_sealant_price_master",
                                   null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = f'{TABLE_PREFIX}SealantPriceMaster'
        
    def __str__(self):
        return self.name
    
    
class Sealant_kit(models.Model):
    sealant_type = models.ForeignKey(Sealant_Types, on_delete=models.PROTECT, related_name="priceing_master_sealant_type")
    normal_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    sealant_markup = models.FloatField(default=0, null=True, blank=True, validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    pricing_master = models.ForeignKey(SealantPriceMaster, on_delete=models.PROTECT, related_name="sealant_kit_master")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Sealant_kit'
    
    def __str__(self):
        return self.sealant_type.sealant_type
    
    
class Surface_finish_Master(models.Model):
    surface_finish_master_name = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Surface_finish_Master'
    
    def __str__(self):
        return self.surface_finish_master_name
    
    
class Surface_finish_kit(models.Model):
    surface_finish_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    surface_finish = models.ForeignKey(Surface_finish, on_delete=models.PROTECT, related_name='kit_surface_finish')
    master = models.ForeignKey(Surface_finish_Master, on_delete=models.PROTECT, related_name='surface_finish_kit_master')
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Surface_finish_kit'
    
    def __str__(self):
        return self.surface_finish.surface_finish