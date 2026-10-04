from django import forms
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)