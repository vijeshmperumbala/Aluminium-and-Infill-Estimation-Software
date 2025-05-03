from django import forms

from apps.pricing_master.models import (
    AdditionalandLabourPriceMaster, 
    PriceMaster, 
    Sealant_kit, 
    SealantPriceMaster, 
    Surface_finish_Master, 
    Surface_finish_kit,
)
from apps.sealant_types.models import Sealant_Types


class CreatePricingForm(forms.ModelForm):

    TYPE = [
        (1, 'International'),
        (2, 'Local'),
    ]

    STATUS = [
        (1, 'Active'),
        (2, 'Inactive'),
    ]

    type = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
                                'class': 'form-select mb-2',
                                'data-control': 'select2',
                                'data-hide-search': 'true',
                                'data-placeholder': 'Status',
                                'data-kt-ecommerce-product-filter': 'status'
                            }))

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
                                'class': 'form-select mb-2',
                                'data-control': 'select2',
                                'data-hide-search': 'true',
                                'data-placeholder': 'Status',
                                'data-kt-ecommerce-product-filter': 'status'
                            }))

    class Meta:
        model = PriceMaster
        fields = ['type',
                  'status',
                  'title',
                  'description',
                  'price_per_kg',
                  'markup',
                  ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Title',
                    'required': True
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description'
                }
            ),
            'price_per_kg': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price/Kg'
                }
            ),
            'markup': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Markup',
                    'required': True
                }
            ),
        }



class EditPricingForm(forms.ModelForm):

    TYPE = [
        (1, 'International'),
        (2, 'Local'),
    ]

    STATUS = [
        (1, 'Active'),
        (2, 'Inactive'),
    ]

    type = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
                                'class': 'form-select mb-2',
                                'data-control': 'select2',
                                'data-hide-search': 'true',
                                'data-placeholder': 'Status',
                                'data-kt-ecommerce-product-filter': 'status'
                            }))

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
                                'class': 'form-select mb-2',
                                'data-control': 'select2',
                                'data-hide-search': 'true',
                                'data-placeholder': 'Status',
                                'data-kt-ecommerce-product-filter': 'status'
                            }))

    class Meta:
        model = PriceMaster
        fields = ['type',
                  'status',
                  'title',
                  'description',
                  'price_per_kg',
                  'markup',
                  ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Title',
                    'id': 'edit_title',
                    'required': True
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'id': 'edit_designation',
                    'required': True
                }
            ),
            'price_per_kg': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price/Kg',
                    'id': 'edit_price_per_kg'
                }
            ),
            'markup': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Pricing Markup',
                    'id': 'edit_markup',
                    'required': True
                }
            ),
        }
        
        

class CreateAdditionalandLabourForm(forms.ModelForm):

    class Meta:
        model = AdditionalandLabourPriceMaster
        fields = [
                  'name',
                  'ideal_overhead',
                  'ideal_labour',
                  'minimum_overhead',
                  'minimum_labour',
                  ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Title',
                    'required': True
                }
            ),
            'ideal_overhead': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ideal Additional Allowance'
                }
            ),
            'ideal_labour': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Ideal Labour'
                }
            ),
            'minimum_overhead': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Minimum Additional Allowance'
                }
            ),
            'minimum_labour': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Minimum Labour'
                }
            )
        }


class CreateSealantForm(forms.ModelForm):
    sealant_type = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(), empty_label='Select an Option')
    sealant_type.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    
    class Meta:
        model = Sealant_kit
        fields = [
            'sealant_type',
            'price',
            'normal_price',
            'sealant_markup'
        ]
        widgets = {
            'price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid sealant_price',
                    'placeholder': 'Sealant Price',
                    'readonly': True,
                }
            ),
            'normal_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid sealant_base',
                    'placeholder': 'Sealant Price'
                }
            ),
            'sealant_markup': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid sealant_markup',
                    'placeholder': 'Sealant Markup',
                }
            ),
            
        }


class EditSealantForm(forms.ModelForm):
    # sealant_type = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(), empty_label='Select an Option')
    # sealant_type.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = SealantPriceMaster
        fields = [
            # 'sealant_type',
            # 'price'
            'name'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Sealant Name'
                }
            ),
            
        }


class CreateSurfaceFinishMaster(forms.ModelForm):
    class Meta:
        model = Surface_finish_Master
        fields = [
            'surface_finish_master_name',
        ]
        widgets = {
            'surface_finish_master_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Name'
                }
            ),
        }
        
        
# class CreateSurfaceFinishKit(forms.ModelForm):
#     class Meta:
#         model = Surface_finish_kit
#         fields = [
#             'surface_finish_price',
#             'surface_finish',
#         ]
#         widgets = {
#             'surface_finish_price': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'placeholder': 'Price'
#                 }
#             ),
#         }