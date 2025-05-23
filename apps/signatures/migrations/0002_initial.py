# Generated by Django 3.2.4 on 2025-04-20 07:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('signatures', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('designations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signatures',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_by_signature', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='signatures',
            name='designation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='signature_designation', to='designations.designations'),
        ),
        migrations.AddField(
            model_name='signatures',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='signatures',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='signature_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
