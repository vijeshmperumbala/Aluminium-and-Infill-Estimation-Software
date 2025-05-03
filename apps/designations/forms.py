from django import forms

from apps.designations.models import Designations


class CreateDesignationForm(forms.ModelForm):
    class Meta:
        model = Designations
        fields = ['designation']
        widgets = {
            'designation': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Designation',
                    'required': True
                }
            )
        }


class EditDesignationForm(forms.ModelForm):
    class Meta:
        model = Designations
        fields = ['designation']
        widgets = {
            'designation': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_designation_form',
                    'required': True
                }
            )
        }
