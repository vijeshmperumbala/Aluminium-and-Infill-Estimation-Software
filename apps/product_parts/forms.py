from django import forms
from apps.brands.models import CategoryBrands

from apps.product_parts.models import Parts, Product_Parts_Kit, Profile_Kit, Profile_items
from apps.profiles.models import ProfileMasterSeries, ProfileMasterType, Profiles


class CreatePartsForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['parts_name']
        widgets = {
            'parts_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mt-0',
                    'placeholder': 'Parts Name',
                    'required': True
                }
            )
        }


class CreateProfilesKit(forms.ModelForm):
    def __init__(self, *args, product=None, **kwargs):
        super(CreateProfilesKit, self).__init__(*args, **kwargs)
        self.fields['system'].empty_label = "Systems"
        self.fields['system'].queryset = CategoryBrands.objects.filter(category=product.product_category) 
        self.fields['system'].widget.attrs.update({
                'class': 'form-control form-control-solid form-select',
                'data-placeholder': 'Select an option'
            })
        self.fields['parts_kit'].empty_label = "Parts Kit"
        self.fields['parts_kit'].queryset = Product_Parts_Kit.objects.filter(product=product) 
        self.fields['parts_kit'].widget.attrs.update({
                'class': 'form-control form-control-solid form-select',
                'data-placeholder': 'Select an option'
            })
        
        
    profile_type = forms.ModelChoiceField(queryset=ProfileMasterType.objects.all(), empty_label="Select a Profile Type")
    profile_type.widget.attrs.update({
        'class': 'form-control form-control-solid form-select',
        'data-placeholder': 'Select an option'
    })
    
    profile_series = forms.ModelChoiceField(queryset=ProfileMasterSeries.objects.all(), empty_label="Select a Series")
    profile_series.widget.attrs.update({
        'class': 'form-control form-control-solid form-select',
        'data-placeholder': 'Select an option'
    })
    
    # system = forms.ModelChoiceField(queryset=CategoryBrands.objects.filter(category=category), empty_label="Select a Profile")
    # system.widget.attrs.update({
    #     'class': 'form-control form-control-solid profile_data',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = Profile_Kit
        fields = [
            "profile_name",
            "kit_weight_lm",
            "system",
            "profile_type",
            "profile_series",
            "parts_kit"
        ]
        widgets = {
            'profile_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Profile Name',
                    'type': 'hidden',
                }
            ),
            'kit_weight_lm': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Weight Per Linear Meater'
                }
            ),

        }

def CreateKitParts(category):
    class KitProfileItemsForm(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(KitProfileItemsForm, self).__init__(*args, **kwargs)
            self.fields['parts'].empty_label = "parts"
            self.fields['parts'].queryset = Parts.objects.filter(parts_category=category) 
            self.fields['parts'].widget.attrs.update({
                    'class': 'form-control floating-control invoice_stage',
                    'data-placeholder': 'Select an option'
                })
            
            
            self.fields['profile'].empty_label = "Profile"
            self.fields['profile'].queryset = Profiles.objects.filter(profile_enable=True, profile_master_series__profile_master_type__profile_master_category=category) 
            self.fields['profile'].widget.attrs.update({
                    'class': 'form-control floating-control profile_data',
                    'data-placeholder': 'Select an Profile'
                })
            
            self.fields['system'].empty_label = "System"
            self.fields['system'].queryset = CategoryBrands.objects.filter(category=category) 
            self.fields['system'].widget.attrs.update({
                    'class': 'form-control floating-control system_select',
                    'data-placeholder': 'Select an Profile'
                })
                
        
        # profile = forms.ModelChoiceField(queryset=Profiles.objects.filter(profile_enable=True), empty_label="Select a Profile")
        # profile.widget.attrs.update({
        #     'class': 'form-control form-control-solid profile_data',
        #     'data-placeholder': 'Select an option'
        # })
        
        # parts = forms.ModelChoiceField(queryset=Parts.objects.select_related(), empty_label="Select a Part")
        # parts.widget.attrs.update({
        #     'class': 'form-control form-control-solid',
        #     'data-placeholder': 'Select an option'
        # })
        
        
        class Meta:
            model = Profile_items
            fields = [
                "formula",
                "profile",
                "parts",
                "system"
            ]
            widgets = {
                'formula': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid',
                        'placeholder': 'Profile Formula',
                        'required': True
                    }
                ),
            }
    return KitProfileItemsForm