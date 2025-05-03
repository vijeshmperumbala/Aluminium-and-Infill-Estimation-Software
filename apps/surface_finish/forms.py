from django import forms

from apps.surface_finish.models import Surface_finish, SurfaceFinishColors


class CreateSurfaceFinishForm(forms.ModelForm):
    class Meta:
        model = Surface_finish
        fields = ['surface_finish']
        widgets = {
            'surface_finish': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Surface Finish',
                    'reuired': True
                    
                }
            ),
            # 'surface_finish_price': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid',
            #         'placeholder': 'Price'
            #     }
            # )
        }


class EditSurfaceFinishForm(forms.ModelForm):
    class Meta:
        model = Surface_finish
        fields = ['surface_finish']
        widgets = {
            'surface_finish': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_surface_finish_form',
                }
            ),
            # 'surface_finish_price': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid edit_surface_finish_price_form',
            #     }
            # )
        }
        
class SurfaceFinishColorsForm(forms.ModelForm):
    class Meta:
        model = SurfaceFinishColors
        fields = ['color']
        widgets = {
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                }
            ),
            
        }