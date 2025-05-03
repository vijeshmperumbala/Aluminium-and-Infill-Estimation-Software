from django import forms

from apps.project_specifications.models import ProjectSpecifications

class CreateProjectSpecificationsForm(forms.ModelForm):
    class Meta:
        model = ProjectSpecifications
        fields = ['specification']
        widgets = {
            'specification': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Project Specification name'
                }
            ),
        }


class EditProjectSpecificationsForm(forms.ModelForm):
    class Meta:
        model = ProjectSpecifications
        fields = ['specification']
        widgets = {
            'specification': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_project_spec',
                    'placeholder': 'Project Specification name'
                }
            ),
        }