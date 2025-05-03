from django import forms

from apps.customers.models import Customers, Contacts
from apps.brands.models import Countries
from apps.designations.models import Designations


class CreateCustomerForm(forms.ModelForm):

    TYPE = [
        (1, 'Company'),
        (2, 'Individual'),
    ]

    customer_type = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
                                    'class': 'form-select mb-2',
                                    # 'data-control': 'select2',
                                    'data-hide-search': 'true',
                                    'data-placeholder': 'Status',
                                    'data-kt-ecommerce-product-filter': 'status'
                                }))

    country = forms.ModelChoiceField(queryset=Countries.objects.all(), initial=1)
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        # 'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_add_customer',
        'data-placeholder': 'Select a Country...'
    })

    class Meta:
        model = Customers
        fields = [
                    'name',
                    'official_email',
                    'official_number',
                    'description',
                    'location',
                    'country',
                    'customer_type',
                    'address'
                ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Company/Customer Name',
                    'required': True
                }
            ),
            'official_email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Official Email',
                    'required': True
                }
            ),
            'official_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Official Number',
                    'required': True
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Description'
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Location'
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Address',
                    'rows': 3,
                }
            ),

        }


class EditCustomerForm(forms.ModelForm):

    country = forms.ModelChoiceField(queryset=Countries.objects.all(), initial=1)
    country.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_add_customer',
        'data-placeholder': 'Select a Country...'
    })

    class Meta:
        model = Customers
        fields = [
                    'name',
                    'official_email',
                    'official_number',
                    'description',
                    'location',
                    'country',
                    'image',
                    'address'
                ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Company/Customer Name',
                    'required': True
                }
            ),
            'official_email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Official Email',
                    'required': True
                }
            ),
            'official_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Official Number',
                    'required': True
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Description'
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Location',
                    'required': True
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Address',
                    'rows': 3,
                }
            ),


        }


class CreateContactForm(forms.ModelForm):

    designation = forms.ModelChoiceField(queryset=Designations.objects.all(), initial=1)
    designation.widget.attrs.update({
        'class': 'form-select mb-2',
        # 'data-control': 'select2',
        # 'data-dropdown-parent': '#kt_modal_add_contact, #kt_modal_add_customer',
        'data-placeholder': 'Select a Designation...'
    })
    
    SALUTATIONS_CHOICES = (
        (1, 'Mr.'),
        (2, 'Mrs.'),
        (3, 'Miss'),
        (4, 'Ms.'),
        (5, 'Dr.'),
        (6, 'Prof.'),
        (7, 'Sir'),
        (8, 'Madam'),
        (9, 'Ma\'am'),
        # (10, 'Dear'),
        (11, 'Eng.'),
        (12, 'Sheikh'),
        (13, 'Sheikha'),
    )
    sorted_choices = sorted(SALUTATIONS_CHOICES, key=lambda x: x[1])
    salutation = forms.ChoiceField(choices=sorted_choices, widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-placeholder': 'Salutation',
            'data-kt-ecommerce-product-filter': 'salutation'
        }))

    class Meta:
        model = Contacts
        fields = [
                    'first_name',
                    'last_name',
                    'email',
                    'mobile_number',
                    'is_primary',
                    'designation',
                    'salutation',
                    
                ]

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter First Name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Last Name'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Email',
                    "required": True,
                }
            ),
            'mobile_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Contact Number',
                    "required": True,
                }
            ),
            'is_primary': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }


class EditContactForm(forms.ModelForm):

    designation = forms.ModelChoiceField(queryset=Designations.objects.all(), initial=1)
    designation.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-control': 'select2',
        'data-dropdown-parent': '#kt_modal_add_contact',
        'data-placeholder': 'Select a Designation...'
    })
    SALUTATIONS_CHOICES = (
        (1, 'Mr.'),
        (2, 'Mrs.'),
        (3, 'Miss'),
        (4, 'Ms.'),
        (5, 'Dr.'),
        (6, 'Prof.'),
        (7, 'Sir'),
        (8, 'Madam'),
        (9, 'Ma\'am'),
        # (10, 'Dear'),
        (11, 'Eng.'),
        (12, 'Sheikh'),
        (13, 'Sheikha'),
    )
    sorted_choices = sorted(SALUTATIONS_CHOICES, key=lambda x: x[1])
    salutation = forms.ChoiceField(choices=sorted_choices, widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-placeholder': 'Salutation',
            'data-kt-ecommerce-product-filter': 'salutation'
        }))

    class Meta:
        model = Contacts
        fields = [
                    'first_name',
                    'last_name',
                    'email',
                    'mobile_number',
                    'designation',
                    'salutation',
                    'is_primary',
                    
                ]

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter First Name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Last Name'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Email'
                }
            ),
            'mobile_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enter Contact Number',
                }
            ),
            'is_primary': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }
