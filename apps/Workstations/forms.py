from django import forms

from apps.Workstations.models import Workstations


class CreateWorkstationsForm(forms.ModelForm):
    class Meta:
        model = Workstations
        fields = ['work_station']
        widgets = {
            'work_station': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Workstation Name',
                    # 'required': True,
                }
            )
        }


class EditWorkstationsForm(forms.ModelForm):
    class Meta:
        model = Workstations
        fields = ['work_station']
        widgets = {
            'work_station': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_workstation_form',
                    # 'required': True,
                    
                }
            )
        }