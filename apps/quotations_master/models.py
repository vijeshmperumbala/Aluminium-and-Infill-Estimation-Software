from email.policy import default
from django.db import models
from apps.companies.models import Companies
from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX


class Quotations_Master(BaseModel):

    TYPE = [
        (1, 'General'),
        (2, 'Short'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_quotation_master")
    q_type = models.IntegerField(choices=TYPE, null=True, blank=True)
    master_remarks = models.CharField(max_length=2000, null=True, blank=True)
    short_terms_and_conditions = models.CharField(max_length=6000, null=True, blank=True)
    general_terms_and_conditions = models.CharField(max_length=6000, null=True, blank=True)
    short_description = models.CharField(max_length=2000, null=True, blank=True)
    general_description = models.CharField(max_length=2000, null=True, blank=True)
    master_terms_of_payment = models.CharField(max_length=2000, null=True, blank=True)
    master_exclusions = models.CharField(max_length=2000, null=True, blank=True)
    template_name = models.CharField(max_length=225)
    company = models.ForeignKey(Companies, on_delete=models.PROTECT, null=True, blank=True, related_name="quotation_temp_company")

    class Meta:
        db_table = f'{TABLE_PREFIX}Quotations_Master'
