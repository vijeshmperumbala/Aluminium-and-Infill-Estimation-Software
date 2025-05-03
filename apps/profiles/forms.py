from django import forms
from apps.product_parts.models import Parts
from apps.profile_types.models import Profile_Types

from apps.profiles.models import ProfileMasterSeries, Profiles, ProfileMasterType


class CreateProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super(CreateProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_master_part'].queryset = Parts.objects.filter(parts_category=category)
        self.fields['profile_master_part'].widget.attrs.update({
            'class': 'form-control floating-control mt-0',
            'data-placeholder': 'Select an option'
        })
        self.fields['profile_master_part'].empty_label = 'Select Parts'
    
    class Meta:
        model = Profiles
        fields = [
            'profile_code',
            'thickness',
            'weight_per_lm',
            'profile_enable',
            'profile_master_part'
            ]
        widgets = {
            'profile_code': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mt-0',
                    'placeholder': 'Profile Code',
                    'required': True
                }
            ),
            'thickness': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mt-0',
                    'placeholder': 'Thickness',
                    'required': True
                }
            ),
            'weight_per_lm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mt-0',
                    'placeholder': 'Weight per LM'
                }
            ),
            'profile_enable': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px me-3',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
        }

class CreateProfileMasterType(forms.ModelForm):
    profile_master_type = forms.ModelChoiceField(queryset=Profile_Types.objects.all(), empty_label="Select a Profile Type")
    profile_master_type.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option'
    })
    class Meta:
        model = ProfileMasterType
        fields = [
            'profile_master_type',
        ]
        
class CreateProfileMasterSeries(forms.ModelForm):
    class Meta:
        model = ProfileMasterSeries
        fields = [
            'profile_master_series'
        ]
        widgets = {
            'profile_master_series': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Profile Series',
                    'required': True
                }
            ),
        }