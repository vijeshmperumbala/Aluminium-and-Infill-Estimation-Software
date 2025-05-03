from django import forms

from apps.provisions.models import Provisions


class CreateProvisionsForm(forms.ModelForm):
    class Meta:
        model = Provisions
        fields = ['provisions', 'provisions_price']
        widgets = {
            'provisions': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Provisions name'
                }
            ),
            'provisions_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Provisions Price'
                }
            )
        }


class EditProvisionsForm(forms.ModelForm):
    class Meta:
        model = Provisions
        fields = ['provisions', 'provisions_price']
        widgets = {
            'provisions': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_provisions_form',
                }
            ),
            'provisions_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_provisions_price_form',
                }
            )
        }