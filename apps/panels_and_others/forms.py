from django import forms
from django.db.models import Q

from apps.accessories_kit.models import AccessoriesKit
from apps.panels_and_others.models import PanelMasterBase, PanelMasterBrands, PanelMasterSeries, \
    PanelMasterSpecifications, PanelMasterConfiguration
from apps.brands.models import CategoryBrands, Countries, AccessoriesBrands
from apps.product_master.models import Product
from apps.Categories.models import Category


class CreatePanelMasterBaseForm(forms.ModelForm):
    # two_D=True
    panel_category = forms.ModelChoiceField(queryset=Category.objects.filter(Q(one_D=False,two_D=True)), empty_label="Select a Category")
    panel_category.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = PanelMasterBase
        fields = ['panel_category']
        # widgets = {
        #     'brand': forms.TextInput(
        #         attrs={
        #             'class': 'form-control form-control-solid',
        #             'placeholder': 'Brand Name'
        #         }
        #     )
        # }


class CreatePanelMasterBrandsForm(forms.ModelForm):
    panel_brands = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), empty_label="Select a Brand")
    panel_brands.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = PanelMasterBrands
        fields = ['panel_brands']


class CreatePanelMasterSeriesForm(forms.ModelForm):
    # series = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all(), empty_label="Select a Brand")
    class Meta:
        model = PanelMasterSeries
        fields = ['series']
        widgets = {
            'series': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Panel Series',
                    'required': True
                }
            )
        }


class AddGlassSpecificationsFrom(forms.ModelForm):
    GLASS_TYPE = [
        (1, 'Double Glass Unit'),
        (2, 'Single Glass')
    ]

    glass_type = forms.ChoiceField(choices=GLASS_TYPE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Glass Type',
    }))

    class Meta:
        model = PanelMasterSpecifications
        fields = ['specifications', 'glass_type', 'outer', 'air_space', 'inner']
        widgets = {
            'specifications': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Panel Specification',
                    'required': True
                }
            ),
            'outer': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid specifications_data',
                    'placeholder': 'Panel Series'
                }
            ),
            'air_space': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid specifications_data',
                    'placeholder': 'Panel Series'
                }
            ),
            'inner': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid specifications_data',
                    'placeholder': 'Panel Series'
                }
            ),
        }


class AddPanelSpecificationsFrom(forms.ModelForm):

    class Meta:
        model = PanelMasterSpecifications
        fields = ['specifications']
        widgets = {
            'specifications': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Panel Specification',
                    'required': True
                }
            )
        }


class AddPanelConfigurationFrom(forms.ModelForm):

    STATUS = [
        (1, 'Active'),
        (2, 'Inactive')
    ]

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))

    class Meta:
        model = PanelMasterConfiguration
        fields = [
                  'title',
                  'description',
                  'status',
                  'date',
                  'min_price_and_area_req',
                  'min_price',
                  'markup_percentage_req',
                  'markup_percentage',
                  'min_area',
                  'price_per_sqm',
                  'u_value',
                  'shading_coefficient',
                  'panel_quoted_rate',
                  ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Panel Title',
                    'required': True
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Panel Series'
                }
            ),
            'min_price_and_area_req': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'min_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Input the minimum price'
                }
            ),
            'price_per_sqm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price per SqM'
                }
            ),
            'min_area': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Input the minimum area'
                }
            ),
            'markup_percentage_req': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Input the %'
                }
            ),
            
            'u_value': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Input the U Value'
                }
            ),
            'shading_coefficient': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Input the Shading Coefficient'
                }
            ),
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date'
                }
            ),

        }


# class AddPanelConfigurationPriceFrom(forms.ModelForm):
#
#     PRICE = [
#         (1, 'Price/SqM'),
#         (2, 'Price/Unit')
#     ]
#
#     price_category = forms.ChoiceField(choices=PRICE, widget=forms.Select(attrs={
#         'class': 'form-select form-select-solid',
#         'data-control': 'select2',
#     }))
#
#     class Meta:
#         model = PanelMasterPrice
#         fields = ['price_category', 'price']
#         widgets = {
#             'price': forms.TextInput(
#                 attrs={
#                     'class': 'form-control mb-2',
#                     'placeholder': 'Price'
#                 }
#             ),
#         }
