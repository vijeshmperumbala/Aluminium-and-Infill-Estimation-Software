from django import forms

from apps.vehicles_and_drivers.models import Vehicles, Drivers


class CreateVehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicles
        fields = ['vehicle_name']
        widgets = {
            'vehicle_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Vehicle Name',

                }
            )
        }


class CreateDriverForm(forms.ModelForm):

    class Meta:
        model = Drivers
        fields = ['driver']
        widgets = {
            'driver': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Driver Name',

                }
            )
        }
