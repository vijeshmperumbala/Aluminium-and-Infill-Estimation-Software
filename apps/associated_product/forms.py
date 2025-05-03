from django import forms

from apps.associated_product.models import AssociatedProducts


class CreateAssociatedProductForm(forms.ModelForm):
    class Meta:
        model = AssociatedProducts
        fields = [
            'product_name',
        ]
        widgets = {
            'product_name': forms.TextInput(
                attrs={
                    'class': 'form-control mb-2',
                    'placeholder': 'Associated Product Name'
                }
            ),
        }