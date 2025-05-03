from django import forms

from apps.others.models import (
    Labour_and_OverheadMaster, 
    SubmittingParameters,
)
from apps.projects.models import EPSBuildingsModel, ElevationModel, FloorModel



class CreateSubmitParameterForm(forms.ModelForm):
    class Meta:
        model = SubmittingParameters
        fields = [
                    'parameter_name',
                ]
        widgets = {
            'parameter_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Parameter'
                }
            ),
        }

    
        
        
class CreateLabour_and_OverheadPercentage(forms.ModelForm):
    class Meta:
        model = Labour_and_OverheadMaster
        fields = [
                    "labour_percentage",
                    "overhead_percentage",
                ]
        widgets = {
            'labour_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Labour Percentage',
                }
            ),
            'overhead_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Overhead Percentage',
                }
            ),
        }
        
class CreateElevation(forms.ModelForm):
    class Meta:
        model = ElevationModel
        fields = '__all__'
        widgets = {
            'elevation': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Elevation Type',
                }
            ),
        }
    
    
class CreateProjectBuilding(forms.ModelForm):
    class Meta:
        model = EPSBuildingsModel
        fields = [
                'building_name',
            ]
        widgets = {
            'building_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Building Name',
                }
            ),
        }


class CreateProjectFloor(forms.ModelForm):
    class Meta:
        model = FloorModel
        fields = [
                'floor_name',
            ]
        widgets = {
            'floor_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Floor Name',
                }
            ),
        }