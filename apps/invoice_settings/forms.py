from django import forms

from apps.invoice_settings.models import Invoice_Settings


class CreateInvoiceSettingsForm(forms.ModelForm):
    class Meta:
        model = Invoice_Settings
        fields = ['invoice_stage']
        widgets = {
            'invoice_stage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Invoice Stage',
                    'required': True
                }
            )
        }


class EditInvoiceSettingsForm(forms.ModelForm):
    class Meta:
        model = Invoice_Settings
        fields = ['invoice_stage']
        widgets = {
            'invoice_stage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_invoice_stage_form',
                    'required': True
                }
            )
        }