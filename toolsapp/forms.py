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
            'payment_method'
            
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

# class AdminLoginForm()

class ProductForm(ModelForm):
    more_image=forms.FileField(required=False,widget=forms.FileInput(attrs={
        "class":"form-control",
        "multiple":True
    }))
    class Meta:
        model=Product
        fields=[
            "title",
            "slug",
            "category",
            "image",
            "marked_price",
            "sell_price",
            "description",
            "warranty",
            "return_policy"
        ]
        widgets = {
            "title":forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Product Title"
            }),
            "slug":forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Product Unique slug"
            }),
            "category":forms.Select(attrs={
            "class":"form-control"
            }),
            "image":forms.ClearableFileInput(attrs={
            "class":"form-control"
            }),
            "marked_price":forms.NumberInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Marked Price of this Product"
            }),
            "sell_price":forms.NumberInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Selling Price of this Product"
            }),
            "description":forms.Textarea(attrs={
            "class":"form-control",
            "placeholder":"Description of this Product",
            "rows":4
            }),
            "warranty":forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Product Warranty"
            }),
            "return_policy":forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Product Return_policy"
            }),
        }