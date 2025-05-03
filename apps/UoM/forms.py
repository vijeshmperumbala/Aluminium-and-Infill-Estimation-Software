from django import forms

from apps.UoM.models import UoM


class CreateUoMForm(forms.ModelForm):
    class Meta:
        model = UoM
        fields = ['uom']
        widgets = {
            'uom': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'UoM',
                    'required': True,
                }
            )
        }


class EditUoMForm(forms.ModelForm):
    class Meta:
        model = UoM
        fields = ['uom']
        widgets = {
            'uom': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_uom_form',
                    'required': True,
                    
                }
            )
        }