from .models import *
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model=User
        fields=[
            'username',
            'email',
            'first_name',
            'password1',
            'password2'
            ]

class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=[
            'name',
            'email',
            'phone',
            'quantity',
            'postal_code',
            'village',
            'district',
            'division'
            ]