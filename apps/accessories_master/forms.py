from django import forms

from apps.accessories_master.models import Accessories
from apps.brands.models import Countries, AccessoriesBrands
from apps.UoM.models import UoM


class CreateAccessoriesForm(forms.ModelForm):
    STATUS = [
        (1, 'Published'),
        (2, 'Draft'),
        (3, 'Scheduled'),
        (4, 'Inactive')
    ]

    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), initial=1)
    uom.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Select an option',
        'required': True
    })

    country = forms.ModelChoiceField(
        queryset=Countries.objects.all(), empty_label='Select a Country')
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_activities1',
        'data-placeholder': 'Select a Country',
        'id': 'id_country_acc_brand',
        'required': True
    })

    accessory_brand = forms.ModelChoiceField(
        queryset=AccessoriesBrands.objects.all())
    accessory_brand.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Select a brand',
        'required': True
    })

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))

    class Meta:
        model = Accessories
        fields = ['accessory_name',
                  'uom',
                  'description',
                  'image',
                  'status',
                  'country',
                  'accessory_brand',
                #   'formula'
                  ]
        widgets = {
            'accessory_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Accessory name'
                }
            ),
            # 'formula': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2',
            #         'placeholder': 'Formula'
            #     }
            # ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Accessory Description',
                    'rows': 4,
                    'cols': 50,
                    'required': True
                }
            )

        }


class EditAccessoriesForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput, required=False)
    STATUS = [
        (1, 'Published'),
        (2, 'Draft'),
        (3, 'Scheduled'),
        (4, 'Inactive')
    ]

    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), initial=1)
    uom.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Select an option',
        'required': True
    })

    country = forms.ModelChoiceField(
        queryset=Countries.objects.all(), initial=1)
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_activities1',
        'data-placeholder': 'Select a Country...',
        'id': 'id_country_acc_brand',
        'required': True
    })

    accessory_brand = forms.ModelChoiceField(
        queryset=AccessoriesBrands.objects.all(), initial=1)
    accessory_brand.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-placeholder': 'Select an option',
        'required': True
    })

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))

    class Meta:
        model = Accessories
        fields = ['accessory_name',
                  'uom',
                  'description',
                  'image',
                  'status',
                  'country',
                  'accessory_brand',
                #   'formula'
                  ]
        widgets = {
            'accessory_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Accessory name',
                    'required': True
                }
            ),
            # 'formula': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2',
            #         'placeholder': 'Formula'
            #     }
            # ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Accessory Description',
                    'rows': 4,
                    'cols': 50,
                    'required': True
                }
            )
        }
