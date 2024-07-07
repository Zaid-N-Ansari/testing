from django.conf import settings
from .models import UserAccount
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import (
	AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)

class LoginForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        strip=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password confirmation",
        strip=False,
    )

    class Meta:
        model = UserAccount
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autofocus':'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'autofocus':'false'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserAccount.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already in Use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserAccount.objects.filter(username=username).exists():
            raise forms.ValidationError("Username Already in Use.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
        return user


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.CharField(
        label = 'Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'class':'form-control'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not UserAccount.objects.filter(email=email).exists():
            raise ValidationError("This email address is not registered.")
        return email


class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password",
        strip=False,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password confirmation",
        strip=False,
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("The two password fields didn’t match.")
            user = self.user
            if user.check_password(new_password1):
                raise forms.ValidationError("The new password cannot be the same as the current password.")

        return new_password2
    

# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
#     first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

#     class Meta:
#         model = UserAccount
#         fields = ("username", "email", "first_name", "last_name", "password1", "password2")
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
#             'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
#         }

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         if commit:
#             user.save()
#         return user
