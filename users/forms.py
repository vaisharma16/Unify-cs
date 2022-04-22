from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required = True, max_length = 50)
    last_name = forms.CharField(required = True, max_length = 50)
    # Institute_Name = forms.CharField(required = True, max_length = 100)
    # Institute_Area = forms.CharField(required = True, max_length = 100)
    # phone = forms.DecimalField(required = True, max_digits= 10, decimal_places= 0)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required = True, max_length = 50)
    last_name = forms.CharField(required = True, max_length = 50)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']#'email']

class ProfileUpdateForm(forms.ModelForm):
    # bio = forms.CharField(widget= forms.Textarea)
    # firstname = forms.CharField(required = True, max_length = 50)
    # lastname = forms.CharField(required = True, max_length = 50)
    # Institute_Name = forms.CharField(required = False, max_length = 100)
    # Institute_Area = forms.CharField(required = False, max_length = 100)
    # phone = forms.DecimalField(required = False, max_digits= 10, decimal_places= 0)

    class Meta:
        model = Profile 
        fields = ['Institute_Name', 'Institute_Area', 'phone', 'bio', 'image']

