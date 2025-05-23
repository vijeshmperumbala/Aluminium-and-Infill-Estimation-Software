# Generated by Django 3.2.4 on 2025-04-20 07:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AI_RatingModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activated', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_date', models.DateTimeField(blank=True, null=True)),
                ('label', models.IntegerField(blank=True, choices=[(1, 'EXCELLENT'), (2, 'GOOD'), (3, 'AVERAGE'), (4, 'BELOW AVERAGE'), (5, 'POOR')], null=True)),
                ('from_value', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)),
                ('to_value', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)),
            ],
            options={
                'db_table': 'amoeba__AI_Rating',
            },
        ),
        migrations.CreateModel(
            name='Labour_and_OverheadMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('labour_percentage', models.DecimalField(decimal_places=2, max_digits=30)),
                ('overhead_percentage', models.DecimalField(decimal_places=2, max_digits=30)),
            ],
            options={
                'db_table': 'amoeba__Labour_and_OverheadMaster',
            },
        ),
        migrations.CreateModel(
            name='SubmittingParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activated', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_date', models.DateTimeField(blank=True, null=True)),
                ('parameter_name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'amoeba__Submitting_Parameters',
            },
        ),
    ]
