from django import forms

from apps.shopfloors.models import Shopfloors



class ShopFloorForm(forms.ModelForm):
    class Meta:
        model = Shopfloors
        fields = [
            'shopfloor_name'
        ]
        widgets = {
            'shopfloor_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Shop Floor Name'
                }
            )
        }