from django import forms

from apps.accessories_kit.models import AccessoriesKit, AccessoriesKitItem
from apps.accessories_master.models import Accessories
from apps.product_master.models import Product_Accessories


class CreateAccessoryKitForm(forms.ModelForm):

    # KIT_TYPE = [
    #     (1, 'Celestial'),
    #     (2, 'Premium'),
    #     (3, 'Standard'),
    #     (4, 'Normal')
    # ]

    # kit_type = forms.ChoiceField(choices=KIT_TYPE, widget=forms.Select(attrs={
    #     'class': 'form-select mb-2',
    #     # 'data-control': 'select2',
    #     'data-hide-search': 'true',
    #     'data-placeholder': 'Status',
    #     'data-kt-ecommerce-product-filter': 'status'
    # }))
    
    # accessory = forms.ModelChoiceField(queryset=Product_Accessories.objects.all(
    # ), required=False, empty_label="Select a Accessory")
    # accessory.widget.attrs.update({
    #     'class': 'form-select mb-2 kit_acc',
    #     # 'data-control': 'select2',
    #     'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    

    class Meta:
        model = AccessoriesKit
        fields = [
                    "kit_name", 
                    # "kit_type", 
                    "description",
                    # "accessory",
                    # 'model',
                    # 'kit_item_price',
                    # 'quantity',
                    # 'kit_item_total',
                    # 'brand',
                ]
        # fields = ["kit_name", "kit_type", "description", "items"]
        widgets = {
            'kit_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Enter Kit Name',
                    'required': True
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Enter Kit Description',
                    'rows': 4,
                    'cols': 50
                }
            ),
            # 'model': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2',
            #         'placeholder': 'Kit Model'
            #     }
            # ),
            # 'brand': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2',
            #         'placeholder': 'Kit Brand'
            #     }
            # ),
            # 'kit_item_price': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2 kit_price',
            #         'placeholder': 'Kit Price'
            #     }
            # ),
            # 'quantity': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2 kit_quantity',
            #         'placeholder': 'Kit Quantity'
            #     }
            # ),
            # 'kit_item_total': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2 kit_total',
            #         'placeholder': 'Kit Total'
            #     }
            # )
        }


class CreateAccessoryKitItemForm(forms.ModelForm):

    accessory = forms.ModelChoiceField(queryset=Accessories.objects.all(
    ), required=False, empty_label="Select a Accessory")
    accessory.widget.attrs.update({
        'class': 'form-select mb-2 kit_acc d-none',
        # 'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'required': True
    })

    class Meta:
        model = AccessoriesKitItem
        fields = (
            'accessory',
            'model',
            'kit_item_price',
            'quantity',
            'kit_item_total',
            'brand',
            'acce_divisions',
            # 'accessory_formula',
        )

        widgets = {
            'model': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Kit Model'
                }
            ),
            'brand': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Kit Brand'
                }
            ),
            'kit_item_price': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2 kit_price',
                    'placeholder': 'Kit Price',
                    'required': True
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2 kit_quantity',
                    'placeholder': 'Kit Quantity',
                    'required': True
                }
            ),
            'kit_item_total': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2 kit_total',
                    'placeholder': 'Kit Total'
                }
            ),
            'acce_divisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input kit_divisions h-20px w-20px',
                    'placeholder': 'Kit Division'
                }
            ),
            # 'accessory_formula': forms.TextInput(
            #     attrs={
            #         'class': 'form-control mb-2',
            #         'placeholder': 'Kit Formula',
            #         'style': 'display: none', 
                    
            #     }
            # )
        }
