from django.contrib.auth.models import User
from django import forms


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'username', 'password')


class UserStandardLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
