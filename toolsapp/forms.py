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

class CheckoutForm(ModelForm):
    class Meta:
        model=Order
        fields=[
            'ordered_by',
            'shipping_address',
            'phone',
            'email',
            
        ]

class CustomerRegisterForm(ModelForm):
    username=forms.CharField(widget=forms.TextInput())
    password=forms.CharField(widget=forms.PasswordInput())
    email=forms.CharField(widget=forms.EmailInput())

    class Meta:
        model=Customer
        fields=['username',
                'password',
                'email',
                'name',
                'address'
        ]
    def clean_username(self):
        uname=self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('Customer with this name already exists')
        return uname
class CustomerLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput())
    password=forms.CharField(widget=forms.PasswordInput())