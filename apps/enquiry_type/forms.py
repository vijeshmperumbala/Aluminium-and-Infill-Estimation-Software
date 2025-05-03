
from django import forms

from apps.enquiry_type.models import EnquiryTypeModal


class CreateEnquiryTypeForm(forms.ModelForm):
    class Meta:
        model = EnquiryTypeModal
        fields = ['enquiry_type']
        widgets = {
            'enquiry_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enquiry Type',
                }
            )
        }
        
class EditEnquiryTypeForm(forms.ModelForm):
    class Meta:
        model = EnquiryTypeModal
        fields = ['enquiry_type']
        widgets = {
            'enquiry_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_enquiry_type_form',
                }
            )
        }