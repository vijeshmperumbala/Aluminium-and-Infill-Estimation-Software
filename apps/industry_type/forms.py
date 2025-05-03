
from django import forms

from apps.industry_type.models import IndustryTypeModal


class CreateIndustryTypeForm(forms.ModelForm):
    class Meta:
        model = IndustryTypeModal
        fields = ['industry_type']
        widgets = {
            'industry_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Industry Type'
                }
            )
        }
        
class EditIndustryTypeForm(forms.ModelForm):
    class Meta:
        model = IndustryTypeModal
        fields = ['industry_type']
        widgets = {
            'industry_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_industry_type_form',
                }
            )
        }