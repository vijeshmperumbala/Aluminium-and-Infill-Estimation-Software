from django import forms

from apps.brands.models import Brands, CategoryBrands, Countries, AccessoriesBrands
from apps.Categories.models import Category


class CreateCategoryBrandForm(forms.ModelForm):
    # category = forms.ModelChoiceField(
    #     queryset=Category.objects.all(), initial=1)
    # category.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-control': 'select2',
    #     'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })

    country = forms.ModelChoiceField(
        queryset=Countries.objects.all(), initial=1)
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_new_cat_brand_1',
        'data-placeholder': 'Select a Country...',
        'required': True
    })
    
    brands = forms.ModelChoiceField(
        queryset=Brands.objects.all(), initial=1)
    brands.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        
    })

    class Meta:
        model = CategoryBrands
        fields = ['country', 'brands']
        # widgets = {
        #     'brand': forms.TextInput(
        #         attrs={
        #             'class': 'form-control form-control-solid',
        #             'placeholder': 'Brand Name',
        #             'required': True
        #         }
        #     )
        # }


class CreateAccessoryBrandForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Countries.objects.all(), initial=1)
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_new_acc_brand_2',
        'data-placeholder': 'Select a Country...',
        'id': 'id_country_acc_brand',
        'required': True
    })
    
    brands = forms.ModelChoiceField(
        queryset=Brands.objects.all(), initial=1)
    brands.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
    })

    class Meta:
        model = AccessoriesBrands
        fields = ['country', 'brands']
        
        # widgets = {
        #     'brand': forms.TextInput(
        #         attrs={
        #             'class': 'form-control form-control-solid',
        #             'placeholder': 'Brand Name',
        #             'required': True
        #         }
        #     )
        # }


class CreateBaseBrands(forms.ModelForm):
    
    class Meta:
        model = Brands
        fields = [
            'brand_name',
        ]
        
        widgets = {
            'brand_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Brand Name',
                }
            )
        }