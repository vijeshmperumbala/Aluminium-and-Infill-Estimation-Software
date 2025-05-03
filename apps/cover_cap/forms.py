from django import forms
from apps.cover_cap.models import CoverCap_PressurePlates


class CoverCapForm(forms.ModelForm):
    
    class Meta:
        model = CoverCap_PressurePlates
        fields = [
            "cap_name",
            "cap_code",
            "cap_thickness",
            "cap_weight_lm",
            "cap_formula",
        ]
        widgets = {
            'cap_name': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Name',
            }),
            'cap_code': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Code',
            }),
            'cap_thickness': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Thickness',
            }),
            'cap_weight_lm': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Thickness',
            }),
            'cap_formula': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Formula',
            }),
        }