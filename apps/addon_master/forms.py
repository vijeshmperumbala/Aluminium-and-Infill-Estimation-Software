from django import forms

from apps.addon_master.models import Addons


class CreateAddonForm(forms.ModelForm):
    class Meta:
        model = Addons
        fields = ['addon', 'linear_meter', 'sqm', 'unit']
        widgets = {
            'addon': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Addon',
                    'required': True
                }
            ),
            'linear_meter': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price per Linear meter',
                    'required': True
                }
            ),
            'sqm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price per Square meter',
                    'required': True
                }
            ),
            'unit': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Price per Unit'
                }
            ),
        }


class EditAddonForm(forms.ModelForm):
    class Meta:
        model = Addons
        fields = ['addon', 'linear_meter', 'sqm', 'unit']
        widgets = {
            'addon': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_addon_form',
                }
            ),
            'linear_meter': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_linear_meter_form',
                    'placeholder': 'Price per Linear meter'
                }
            ),
            'sqm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_sqm_form',
                    'placeholder': 'Price per Square meter'
                }
            ),
            'unit': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_unit_form',
                    'placeholder': 'Price per Unit'
                }
            ),
        }
