from django import forms

from apps.rating.models import RatingHead


class CreateRatingHeadForm(forms.ModelForm):
    class Meta:
        model = RatingHead
        fields = ['head']
        widgets = {
            'head': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid ',
                }
            ),
        }
