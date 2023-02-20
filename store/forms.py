from django.contrib.auth.models import User
from django import forms

from store.models import Profile, Product


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', 'photo_url')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description')


class UserStandardLoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
