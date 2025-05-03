from django import forms

from apps.tags.models import Tags

class CreateTagForm(forms.ModelForm):
    
    class Meta:
        model = Tags
        fields = ['tag_name']
        widgets = {
            'tag_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Tag',
                    'reuired': True
                    
                }
            )
        }
