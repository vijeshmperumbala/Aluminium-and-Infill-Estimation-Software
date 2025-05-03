from pyexpat import model
from django.db import models
from amoeba.settings import TABLE_PREFIX
from apps.enquiries.models import Enquiries

from apps.user.models import BaseModel


class Suppliers(BaseModel):
    
    supplier_name = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}Suppliers'
        
    def __str__(self):
        return self.supplier_name

        
class BillofQuantity(BaseModel):
    
    boq_number = models.CharField(max_length=255, null=True, blank=True)
    enquiry = models.ForeignKey(Enquiries, on_delete=models.PROTECT, related_name="boq_enquiry", blank=True, null=True)
    
    class Meta:
        db_table = f'{TABLE_PREFIX}BillofQuantity'
        
    def __str__(self):
        return self.boq_number