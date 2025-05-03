from django import forms
from apps.companies.models import Companies

from apps.quotations_master.models import Quotations_Master


class ShortQuotationMasterCreate(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Companies.objects.all(), required=False, empty_label='Select a Company')
    company.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option'
    })
    class Meta:
        model = Quotations_Master
        fields = [
            'short_terms_and_conditions',
            'short_description',
            'master_remarks',
            'template_name',
            'company',
            # 'header_img',
            # 'footer_img',
            ]
        widgets = {
            'short_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '1',
                    'required': True,
                }
            ),
            'short_terms_and_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '15',
                    'required': True,
                    
                }
            ),
            'master_remarks': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '6',
                    'required': True,
                }
            ),
            'template_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Template Name',
                }
            ),
            # 'header_img': forms.FileInput(
            #     attrs={
            #         'accept': '.png, .jpg, .jpeg',
            #         'type': 'file',
            #         'onchange': 'readURL_header(this);',
            #     }
            # ),
            # 'footer_img': forms.FileInput(
            #     attrs={
            #         'accept': '.png, .jpg, .jpeg',
            #         'type': 'file',
            #         'onchange': 'readURL_footer(this);',
            #     }
            # ),
        }


class GeneralQuotationMasterCreate(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Companies.objects.all(), required=False, empty_label='Select a Company')
    company.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option'
    })
    class Meta:
        model = Quotations_Master
        fields = [
            'general_terms_and_conditions',
            'general_description',
            'master_terms_of_payment',
            'master_exclusions',
            'template_name',
            'company',
            # 'header_img',
            # 'footer_img',
            ]
        widgets = {
            'template_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Template Name',
                }
            ),
            'general_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '3'
                }
            ),
            'general_terms_and_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '15'
                }
            ),
            'master_terms_of_payment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '10'
                }
            ),
            'master_exclusions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid tox-target',
                    'cols': '40',
                    'rows': '6'
                }
            ),
            # 'header_img': forms.FileInput(
            #     attrs={
            #         'accept': '.png, .jpg, .jpeg',
            #         'type': 'file',
            #         'onchange': 'readURL_header(this);',
                    
            #     }
            # ),
            # 'footer_img': forms.FileInput(
            #     attrs={
            #         'accept': '.png, .jpg, .jpeg',
            #         'type': 'file',
            #         'onchange': 'readURL_footer(this);',
                    
            #     }
            # ),
        }
