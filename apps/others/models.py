import django
from django.db import models

from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class AI_RatingModel(BaseModel):
    
    LABELS = [
        (1,'EXCELLENT'),
        (2, 'GOOD'),
        (3, 'AVERAGE'),
        (4, 'BELOW AVERAGE'),
        (5, 'POOR'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_ai_rating")
    label = models.IntegerField(choices=LABELS, null=True, blank=True)
    from_value = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    to_value = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}AI_Rating'
        

class SubmittingParameters(BaseModel):
    parameter_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Submitting_Parameters'
        
    def __str__(self):
        return self.parameter_name
    
class Labour_and_OverheadMaster(models.Model):
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    labour_percentage = models.DecimalField(max_digits=30, decimal_places=2)
    overhead_percentage = models.DecimalField(max_digits=30, decimal_places=2)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Labour_and_OverheadMaster'