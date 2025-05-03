from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm

from apps.user.models import User

class CreateUserRoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid', 
                    'placeholder': 'Specify Role Name',
                    'required': True
                    }
                )
        }
        

class LoginForm(forms.Form):
    password = forms.CharField(
                label='password',
                strip=False,
                widget=forms.PasswordInput,
            )
    email = forms.EmailField(
            label='email',
            max_length=255,
            widget=forms.TextInput(attrs={'autofocus': True}),
        )



class CreateUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'image']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid mb-3 mb-lg-0',
                    'placeholder': 'Enter Name',
                    'required': True
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid mb-3 mb-lg-0',
                    'placeholder': 'abcd@amoeba.com',
                    'required': True
                }
                ),
            'image': forms.FileInput(
                attrs={
                    'accept': '.png, .jpg, .jpeg',
                    'type': 'file',
                }
            ),
        }
        

class ChangePasswordFrom(SetPasswordForm):

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg form-control-solid', 'type': 'password', 'align': 'center',}),
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg form-control-solid', 'type': 'password', 'align': 'center',}),
    )

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    # def clean_new_password1(self):
    #     data = self.cleaned_data['new_password1']
    #     if len(data) < 8 or len(data) > 64:
    #         raise forms.forms.ValidationError("New password should have minimum 8 characters and maximum 64 characters")
    #     return data