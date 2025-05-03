from django import forms

from apps.designations.models import Designations
from apps.signatures.models import Signatures


class CreateSignatureForm(forms.ModelForm):
    designation = forms.ModelChoiceField(queryset=Designations.objects.all(), empty_label="Select a Designation")
    designation.widget.attrs.update({
        'class': 'form-select mb-2 ',
        'data-placeholder': 'Select a Designation'
    })

    class Meta:
        model = Signatures
        fields = ['signature', 'designation', 'image']
        widgets = {
            'signature': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid ',
                    'placeholder': 'Name',
                    'required': True
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'signature_image',
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
        }


class EditSignatureForm(forms.ModelForm):
    designation = forms.ModelChoiceField(queryset=Designations.objects.all(), empty_label="Select a Designation")
    designation.widget.attrs.update({
        'class': 'form-select mb-2 edit_designation_form',
        'data-placeholder': 'Select a Designation'
    })

    class Meta:
        model = Signatures
        fields = ['signature', 'designation', 'image']
        widgets = {
            'signature': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_signature_form',
                    'placeholder': 'Name',
                    'required': True
                    
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'signature_image',
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
        }