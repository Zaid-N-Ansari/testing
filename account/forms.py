from typing import Any
from django.conf import settings
from .models import UserAccount
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import (
	AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm
)

class LoginForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')

    username = forms.CharField(label='Username / Email / Id')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password',
        strip=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password confirmation',
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
            raise forms.ValidationError('Email Already in Use.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserAccount.objects.filter(username=username).exists():
            raise forms.ValidationError('Username Already in Use.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # user.backend = settings.AUTHENTICATION_BACKENDS[0]
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
            raise ValidationError('This email address is not registered.')
        return email


class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autofocus':'true'}),
        label='New password',
        strip=False,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New password confirmation',
        strip=False,
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('Both Passwords Do not Match')
            user = self.user
            if user.check_password(new_password1):
                raise forms.ValidationError('You are using this same Password.')
        else:
            raise ValidationError('Both Password Fields are Required.')

        validate_password(new_password1, user=user)

        return new_password2
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label= 'Old Password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'autofocus': True, 'class':'form-control'}
        ),
    )
    new_password1 = forms.CharField(
        label= 'New Password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class':'form-control'}
        ),
    )
    new_password2 = forms.CharField(
        label= 'New Password Confirm',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class':'form-control'}
        ),
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'email', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autofocus':'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class':'form-control d-none', 'onchange':'readURL(this)'})
        }