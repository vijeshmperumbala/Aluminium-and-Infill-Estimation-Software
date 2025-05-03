import django
from apps.user.models import BaseModel, User
from amoeba.settings import TABLE_PREFIX
from apps.brands.models import Countries
from apps.designations.models import Designations
from django.db import models


class Customers(BaseModel):

    TYPE = [
        (1, 'Company'),
        (2, 'Individual'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_customers")
    name = models.CharField(max_length=255)
    official_email = models.EmailField()
    address = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Countries, on_delete=models.PROTECT, related_name="customers_country")
    image = models.ImageField(upload_to='customer/image', null=True, blank=True)
    post_code = models.IntegerField(null=True, blank=True)
    represented_by = models.ForeignKey('customers.Contacts', on_delete=models.PROTECT,
                                       related_name="represented_by_customer", null=True, blank=True)
    customer_type = models.IntegerField(choices=TYPE, null=True, blank=True)
    official_number = models.CharField(max_length=16)

    class Meta:
        db_table = f'{TABLE_PREFIX}Customers'

    def __str__(self):
        return self.name


class Contacts(BaseModel):
    SALUTATIONS_CHOICES = (
        (1, 'Mr.'),
        (2, 'Mrs.'),
        (3, 'Miss'),
        (4, 'Ms.'),
        (5, 'Dr.'),
        (6, 'Prof.'),
        (7, 'Sir'),
        (8, 'Madam'),
        (9, 'Ma\'am'),
        # (10, 'Dear'),
        (11, 'Eng.'),
        (12, 'Sheikh'),
        (13, 'Sheikha'),
    )
    customer = models.ForeignKey(Customers, on_delete=models.PROTECT, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by_contact")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    designation = models.ForeignKey(Designations, on_delete=models.PROTECT, related_name="contact_designation")
    is_primary = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=16, null=True, blank=True)
    salutation = models.IntegerField(choices=SALUTATIONS_CHOICES)

    class Meta:
        db_table = f'{TABLE_PREFIX}Contacts'


class Customer_Log(BaseModel):
    ACTIONS = [
        (1, "Create"),
        (2, "Update"),
        (3, "Delete"),
        (4, "Export"),
        (5, "Download")
    ]
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="customer_log_user")
    message = models.CharField(max_length=225, null=True, blank=True)
    customer = models.ForeignKey(Customers, null=True, blank=True, on_delete=models.CASCADE, related_name="customer_log")
    action = models.IntegerField(choices=ACTIONS, null=True, blank=True)

    class Meta:
        db_table = f'{TABLE_PREFIX}Customer_Log'