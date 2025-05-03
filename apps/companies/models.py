import django
from django.db import models

from apps.user.models import BaseModel, User
from apps.brands.models import Countries
from amoeba.settings import TABLE_PREFIX


class Companies(BaseModel):

    company_name = models.CharField(max_length=255)
    company_email = models.EmailField()
    company_address = models.CharField(max_length=255)
    company_description = models.CharField(
        max_length=255, null=True, blank=True)
    comany_number = models.CharField(max_length=16)
    country = models.ForeignKey(Countries, on_delete=models.PROTECT,
                                null=True, blank=True, related_name="company_country")
    header_img = models.ImageField(upload_to='companies/header_img', null=True, blank=True)
    footer_img = models.ImageField(upload_to='companies/footer_img', null=True, blank=True)
    
    theme_color = models.CharField(max_length=10)
    compny_logo = models.ImageField(upload_to='companies/logos')

    class Meta:
        db_table = f'{TABLE_PREFIX}Companies'

    def __str__(self):
        return self.company_name
