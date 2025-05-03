from django import forms

from apps.sealant_types.models import Sealant_Types


class CreateSealantTypesForm(forms.ModelForm):
    class Meta:
        model = Sealant_Types
        fields = ['sealant_type']
        widgets = {
            'sealant_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Sealant/Gasket Type'
                }
            )
        }


class EditSealantTypesForm(forms.ModelForm):
    class Meta:
        model = Sealant_Types
        fields = ['sealant_type']
        widgets = {
            'sealant_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_sealant_type_form',
                }
            )
        }