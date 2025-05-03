from django import forms
from django.db.models import Q

from apps.configuration_master.models import ConfigurationMasterBase, ConfigurationMasterBrands, \
    ConfigurationsMaster, ConfigurationMasterSeries
from apps.Categories.models import Category
from apps.brands.models import CategoryBrands
from apps.product_parts.models import Parts, Profile_Kit, Product_Parts_Kit, Product_Parts_Kit_Items


class CreateConfigurationCategoryForm(forms.ModelForm):
    config_category = forms.ModelChoiceField(queryset=Category.objects.filter(Q(one_D=True,two_D=True) |
                                                                              Q(one_D=True,two_D=False)),
                                             empty_label="Select a Category")
    config_category.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = ConfigurationMasterBase
        fields = ["config_category"]


class CreateConfigurationBrandForm(forms.ModelForm):
    brands = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), empty_label="Select a Brand")
    brands.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'required': True
    })

    class Meta:
        model = ConfigurationMasterBrands
        fields = ["brands"]


class CreateConfigurationSeriesForm(forms.ModelForm):
                
    def __init__(self, product, *args, **kwargs):
        super(CreateConfigurationSeriesForm, self).__init__(*args, **kwargs)
        self.fields['config_series'].empty_label = "Select a Series"
        self.fields['config_series'].queryset = Profile_Kit.objects.filter(product=product) 
        self.fields['config_series'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an Series'
            })
        
    class Meta:
        model = ConfigurationMasterSeries
        fields = ['config_series']


class CreateConfigurationMasterForm(forms.ModelForm):

    class Meta:
        model = ConfigurationsMaster
        fields = [
            'title',
            'descriptions',
            'width',
            'height',
            'unit_area',
            'weight_per_unit',
            'min_price_and_area_req',
            'min_price',
            'markup_percentage_req',
            'markup_percentage',
            'price_per_unit',
            'price_per_sqm',
            'enable_weight_per_unit',
            'enable_price_per_sqm',
            'enable_price_per_unit'
        ]
        widgets = {
            
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Configuration Title',
                    'required': True
                }
            ),
            'descriptions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'cols': 50,
                    'rows': 2
                }
            ),
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid measurement',
                    'placeholder': 'Width',
                    'required': True
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid measurement',
                    'placeholder': 'Height',
                    'required': True
                }
            ),
            'unit_area': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Area',
                    'required': True
                }
            ),
            'weight_per_unit': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Weight/Unit',
                    'readonly': True,
                }
            ),
            'price_per_sqm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price/SqM'
                }
            ),
            'price_per_unit': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price/Unit'
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
            'enable_weight_per_unit': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'enable_price_per_sqm': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'enable_price_per_unit': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
        }


class CreateConfigurationProductKit(forms.ModelForm):
    class Meta:
        model = Product_Parts_Kit
        fields = ['kit_name']
        widgets = {
            'kit_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Parts Kit Name',
                    'required': True
                }
            ),
        }
        

def CreateConfiProductKitItem(category):
    class CreateConfigurationProductKititem(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(CreateConfigurationProductKititem, self).__init__(*args, **kwargs)
            self.fields['parts'].queryset = Parts.objects.filter(parts_category=category)
            self.fields['parts'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
            self.fields['parts'].empty_label = 'Select Parts'
            
        class Meta:
            model = Product_Parts_Kit_Items
            fields = [
                "parts",
                "formula",
                "product_parts_kit"
                ]
            widgets = {
                'formula': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid',
                        'placeholder': 'Formula',
                        'required': True
                    }
                ),
            }
    return CreateConfigurationProductKititem