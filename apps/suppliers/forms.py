from django import forms

from apps.suppliers.models import BillofQuantity, Suppliers


class CreateSuppliersForm(forms.ModelForm):

    class Meta:
        model = Suppliers
        fields = [
                    'supplier_name',
                ]
        widgets = {
            'supplier_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Supplier Name',
                    'required': True
                }
            ),

        }


class EditSuppliersForm(forms.ModelForm):

    class Meta:
        model = Suppliers
        fields = [
                    'supplier_name',
                ]
        widgets = {
            'supplier_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid edit_supplier_form',
                    'placeholder': 'Supplier Name',
                    'required': True
                }
            ),

        }


class CreateBoQForm(forms.ModelForm):

    class Meta:
        model = BillofQuantity
        fields = [
                    'boq_number',
                ]
        widgets = {
            'boq_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter BOQ Number',
                    'style': 'line-height: 40px; padding-left: 5px',
                    'required': True
                }
            ),

        }
