from django import forms
from apps.Categories.models import Category
from apps.Workstations.models import Workstations
from apps.accessories_master.models import Accessories
from apps.associated_product.models import AssociatedProducts

from apps.product_master.models import Product, Product_Accessories_Kit, Product_WorkStations, SecondaryProducts
from apps.UoM.models import UoM


class CreateProductForm(forms.ModelForm):
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
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    # TYPE = [
    #     (1, "Primary"),
    #     (2, "Secondary"),
    # ]
    # product_type = forms.ChoiceField(choices=TYPE, initial=1, required=True, widget=forms.RadioSelect(attrs={
    #     'class': 'form-check-input',
    #     'data-placeholder': 'Select an option',
    #     'style': "border: 1px solid #009ef7;",
    # }))

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))
    associated_product = forms.ModelChoiceField(
        queryset=AssociatedProducts.objects.all(), required=False, initial=1)
    associated_product.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = Product
        fields = [
                  'product_name',
                  'uom',
                  'description',
                  'image',
                  'status',
                  'installation_hours',
                  'fabrication_man_hours',

                  'have_associated_product',
                  'associated_product',
                  'have_infill',
                  'assocated_quantity',
                  'infill_quantity',
                  'quotation_product_name',
        	      'min_price',
                #   'product_type',
                ]
        widgets = {
            'have_associated_product': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'have_infill': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product name',
                    'required': True
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Description',
                    'rows': 4,
                    'cols': 20,
                    'required': True
                }
            ),
            'min_price': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Minimum Price',
                }
            ),
            'installation_hours': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Installation Hours',
                    'required': True
                }
            ),
            'fabrication_man_hours': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Fabrication Hours',
                    'required': True
                }
            ),
            'assocated_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Associated Product Qantity',
                }
            ),
            'infill_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Associated Product Qantity',
                }
            ),
            'quotation_product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Name for Quotation',
                }
            ),

        }


class EditProductForm(forms.ModelForm):
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
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    # TYPE = [
    #     (1, "Primary"),
    #     (2, "Secondary"),
    # ]
    # product_type = forms.ChoiceField(choices=TYPE, initial=1, required=True, widget=forms.RadioSelect(attrs={
    #     'class': 'form-check-input',
    #     'data-placeholder': 'Select an option',
    #     'style': "border: 1px solid #009ef7;",
    # }))

    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))
    associated_product = forms.ModelChoiceField(
        queryset=AssociatedProducts.objects.all(), required=False, initial=1)
    associated_product.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = Product
        fields = [
                    'product_name',
                    'uom',
                    'description',
                    'image',
                    'status',
                    'installation_hours',
                    'fabrication_man_hours',
                    'have_associated_product',
                    'associated_product',
                    'have_infill',
                    'infill_quantity',
                    'assocated_quantity',
                    'quotation_product_name',
                    'min_price', 
                    # 'product_type',
                ]
        widgets = {
            'have_associated_product': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'have_infill': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product name',
                    'required': True
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Description',
                    'rows': 4,
                    'cols': 50,
                    'required': True
                }
            ),
            'min_price': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Minimum Price',
                }
            ),
            'installation_hours': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Installation Hours',
                    'required': True
                }
            ),
            'fabrication_man_hours': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Fabrication Hours',
                    'required': True
                }
            ),
            'assocated_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Associated Product Qantity',
                }
            ),
            'infill_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Associated Product Qantity',
                }
            ),
            'quotation_product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Name for Quotation',
                }
            ),

        }


def Product_Accessory_Form(product):
    class ProductAccessoriesCreate(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(ProductAccessoriesCreate, self).__init__(*args, **kwargs)
            self.fields['accessory'].empty_label = "Accessory"
            self.fields['accessory'].queryset = Accessories.objects.filter(
                accessory_category=product.product_category)
            self.fields['accessory'].widget.attrs.update({
                'class': 'form-select mb-2 kit_acc',
                'data-placeholder': 'Select an option',
                'required': False,
            })

        class Meta:
            model = Product_Accessories_Kit
            fields = [
                "accessory",
                "accessory_formula",
            ]
            widgets = {
                'accessory_formula': forms.TextInput(
                    attrs={
                        'class': 'form-control mb-2',
                        'placeholder': 'Accessory Formula',
                        'required': True
                    }
                ),
            }
    return ProductAccessoriesCreate


class CreateProductWorkstations(forms.ModelForm):

    workstation = forms.ModelChoiceField(queryset=Workstations.objects.all(
    ), required=True, empty_label='Select an option')
    workstation.widget.attrs.update({
        'class': 'form-select mb-2',
        'placeholder': 'Select an option'
    })

    class Meta:
        model = Product_WorkStations
        fields = [
            'workstation',
        ]


class CreateSecondaryProduct(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput, required=False)
    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), initial=1)
    uom.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    product_category = forms.ModelChoiceField(queryset=Category.objects.all(), initial=1)
    product_category.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_category',
            'uom',
            'image',
            'description',
        ]
        widgets = {
            'product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product name',
                    'required': True
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Product Description',
                    'rows': 4,
                    'cols': 20,
                    'required': True
                }
            ),
        }
        