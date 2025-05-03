from django import forms

from apps.companies.models import Companies
from apps.brands.models import Countries


class CreateCompanyForm(forms.ModelForm):

    country = forms.ModelChoiceField(queryset=Countries.objects.all(
    ), required=False, empty_label="Select a Country")
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_add_customer',
        'data-placeholder': 'Select a Country...'
    })

    class Meta:
        model = Companies
        fields = [
            'company_name',
            'company_email',
            'company_address',
            'company_description',
            'country',
            'comany_number',
            'header_img',
            'footer_img',
            'theme_color',
            'compny_logo',
        ]
        widgets = {
            'theme_color': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-color w-100px',
                    'placeholder': 'Theme Color',
                    'type': 'color',
                    'value': '#d3363d'
                }
            ),
            'company_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Company Name',
                    'required': True
                }
            ),
            'company_address': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Company Address',
                    'rows': 3,
                    'required': True
                }
            ),
            'company_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Company Description',
                    'rows': 4,
                }
            ),
            'company_email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Official Email',
                    'required': True
                }
            ),
            'comany_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Official Number',
                    'pattern': '[0-9]{8}',
                    'required': True
                }
            ),
            'header_img': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                    'onchange': 'readURL_header(this);',
                }
            ),
            'footer_img': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                    'onchange': 'readURL_footer(this);',
                }
            ),
            'compny_logo': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                    'onchange': 'readURL_logo(this);',
                }
            ),


        }
