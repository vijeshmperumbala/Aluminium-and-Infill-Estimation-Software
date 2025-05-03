import django
from django.contrib.auth.models import AbstractUser
from django.db import models
# from safedelete import SOFT_DELETE_CASCADE
# from safedelete.models import SafeDeleteModel

from amoeba.settings import TABLE_PREFIX
from apps.designations.models import Designations


class User(AbstractUser):

    created_date = models.DateTimeField(default=django.utils.timezone.now)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    designation = models.ForeignKey(
        Designations, on_delete=models.PROTECT, null=True, blank=True)
    image = models.ImageField(upload_to='user/image', null=True, blank=True)
    
    first_name = None
    last_name = None
    
    estimators = models.BooleanField(default=False)
    project_eng = models.BooleanField(default=False)
    production = models.BooleanField(default=False)
    fabrication = models.BooleanField(default=False)
    qaqc = models.BooleanField(default=False)
    procurement = models.BooleanField(default=False)
    delivery = models.BooleanField(default=False)
    inspection = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = f'{TABLE_PREFIX}user'

    def __str__(self):
        return self.name


class BaseModel(models.Model):

    activated = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    last_modified_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        abstract = True
