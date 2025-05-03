from django.db import models
from apps.Categories.models import Category
from apps.brands.models import CategoryBrands
# from apps.product_parts.models import Parts
from apps.profile_types.models import Profile_Types

from apps.user.models import BaseModel
from amoeba.settings import TABLE_PREFIX


class ProfileMasterType(models.Model):
    
    profile_master_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="profile_matser_category", null=True, blank=True)
    profile_master_brand = models.ForeignKey(CategoryBrands, on_delete=models.CASCADE, related_name="profile_matser_category", null=True, blank=True)
    profile_master_type = models.ForeignKey(Profile_Types, on_delete=models.CASCADE, related_name="profile_matser_type")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProfileMasterType'

    def __str__(self):
        return self.profile_master_type.profile_type
    

class ProfileMasterSeries(models.Model):
    
    profile_master_series = models.CharField(max_length=255)
    profile_master_type = models.ForeignKey(ProfileMasterType, on_delete=models.CASCADE, related_name="profile_matser_types")
    
    class Meta:
        db_table = f'{TABLE_PREFIX}ProfileMasterSeries'

    def __str__(self):
        return self.profile_master_series
    

class Profiles(BaseModel):

    profile_code = models.CharField(max_length=255, null=True, blank=True)
    thickness = models.CharField(max_length=255, null=True, blank=True)
    weight_per_lm = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    profile_enable = models.BooleanField(
        default=True, help_text="UnCheck To Disable The Profile.")
    profile_master_series = models.ForeignKey(ProfileMasterSeries, on_delete=models.PROTECT, 
                                              related_name="profile_brand", null=True, blank=True)

    profile_master_part = models.ForeignKey('product_parts.Parts', on_delete=models.PROTECT, related_name="profile_master_part", null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Profiles'

    def __str__(self):
        return self.profile_code
    
