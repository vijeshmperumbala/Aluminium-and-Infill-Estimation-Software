from django import forms

from apps.Categories.models import Category
from apps.associated_product.models import AssociatedProducts
from apps.sealant_types.models import Sealant_Types


class CreateCategoryForm(forms.ModelForm):
    internal_sealant = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Internal Sealant')
    internal_sealant.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Internal Sealant'
    })
    external_sealant = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a External Sealant')
    external_sealant.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a External Sealant'
    })
    
    ployamide_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Ployamide Gasket')
    ployamide_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Ployamide Gasket'
    })
    
    transom_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Transom Gasket')
    transom_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Transom Gasket'
    })
    
    mullion_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Mullion Gasket')
    mullion_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Mullion Gasket'
    })
    
    # epdm_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    # ).order_by('-id'), required=False, empty_label='Select a EPDM Gasket')
    # epdm_gasket.widget.attrs.update({
    #     'class': 'form-control ',
    #     'data-placeholder': 'Select a EPDM Gasket'
    # })
    
    
    class Meta:
        model = Category
        fields = [
            'category',
            'image',
            'one_D',
            'two_D',
            'is_glass',
            'surface_finish',
            'sealant',
            'points_to_remember',
            'points',
            'enable_internal_sealant',
            'enable_external_sealant',
            'internal_sealant',
            'external_sealant',
            'invoice_in_quantity',
            'is_curtain_wall',
            'handrail',
            'window',
            'door',
            'is_ployamide_gasket',
            'is_transom_gasket',
            'is_mullion_gasket',
            # 'is_epdm_gasket',
            'ployamide_gasket',
            'transom_gasket',
            'mullion_gasket',
            # 'epdm_gasket',
            'window_or_door_with_divisions',
            
        ]
        widgets = {
            
            # 'is_epdm_gasket': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-20px',
            #     }
            # ),
            'is_mullion_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_transom_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_ployamide_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'category': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Category Name',
                    'required': True
                }
            ),
            'points': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Points to Remember',
                    'cols': 2,
                    'rows': 10
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
            'one_D': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'two_D': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_glass': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'surface_finish': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_curtain_wall': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'handrail': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'invoice_in_quantity': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'points_to_remember': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'enable_internal_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'enable_external_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'door': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'window': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'window_or_door_with_divisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
        }


class EditCategoryForm(forms.ModelForm):
    internal_sealant = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Internal Sealant')
    internal_sealant.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Internal Sealant',
        'id': 'edit_internal_sealant'
    })
    external_sealant = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a External Sealant')
    external_sealant.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a External Sealant',
        'id': 'edit_external_sealant'

    })
    
    ployamide_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Ployamide Gasket')
    ployamide_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Ployamide Gasket',
        'id': 'edit_id_ployamide_gasket'
        
    })
    
    transom_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Transom Gasket')
    transom_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Transom Gasket',
        'id': 'edit_id_transom_gasket'
        
    })
    
    mullion_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    ).order_by('-id'), required=False, empty_label='Select a Mullion Gasket')
    mullion_gasket.widget.attrs.update({
        'class': 'form-control ',
        'data-placeholder': 'Select a Mullion Gasket',
        'id': 'edit_id_mullion_gasket'
        
    })
    
    # epdm_gasket = forms.ModelChoiceField(queryset=Sealant_Types.objects.all(
    # ).order_by('-id'), required=False, empty_label='Select a EPDM Gasket')
    # epdm_gasket.widget.attrs.update({
    #     'class': 'form-control ',
    #     'data-placeholder': 'Select a EPDM Gasket',
    #     'id': 'edit_id_epdm_gasket'
        
    # })
    

    class Meta:
        model = Category
        fields = [
            'category',
            'image',
            'one_D',
            'two_D',
            'is_glass',
            'surface_finish',
            'sealant',
            'points_to_remember',
            'points',
            'enable_internal_sealant',
            'enable_external_sealant',
            'internal_sealant',
            'external_sealant',
            'invoice_in_quantity',
            'is_curtain_wall',
            'handrail',
            'window',
            'door',
            'is_ployamide_gasket',
            'is_transom_gasket',
            'is_mullion_gasket',
            # 'is_epdm_gasket',
            'ployamide_gasket',
            'transom_gasket',
            'mullion_gasket',
            # 'epdm_gasket',
            'window_or_door_with_divisions',
            
            
        ]
        widgets = {
            
            # 'is_epdm_gasket': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-20px',
            #         'id': 'edit_id_is_epdm_gasket'
            #     }
            # ),
            'is_mullion_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_id_is_mullion_gasket'
                }
            ),
            'is_transom_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_id_is_transom_gasket'
                }
            ),
            'is_ployamide_gasket': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_id_is_ployamide_gasket'
                }
            ),
            'category': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_cat',
                    'placeholder': 'Category',
                    'required': True
                }
            ),
            'points': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Points to Remember',
                    'cols': 2,
                    'rows': 10,
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
            'invoice_in_quantity': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'one_D': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'two_D': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_curtain_wall': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_glass': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'surface_finish': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_id_sealant'
                }
            ),
            'points_to_remember': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_points_to_remember'
                }
            ),
            'handrail': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'enable_internal_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_enable_internal_sealant'
                }
            ),
            'enable_external_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_enable_external_sealant'
                }
            ),
            'window': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_window'
                }
            ),
            'door': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_door'
                }
            ),
            'window_or_door_with_divisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                    'id': 'edit_window_or_door_with_divisions'
                }
            ),
        }
