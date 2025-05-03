from django import forms

from apps.profile_types.models import Profile_Types


class CreateProfileTypeForm(forms.ModelForm):
    class Meta:
        model = Profile_Types
        fields = ['profile_type']
        widgets = {
            'profile_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Profile Types',
                    'required': True
                }
            )
        }


class EditProfileTypeForm(forms.ModelForm):
    class Meta:
        model = Profile_Types
        fields = ['profile_type']
        widgets = {
            'profile_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_profile_type',
                }
            )
        }