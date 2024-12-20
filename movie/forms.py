from django import forms
from .models import CustomUser

class SignupForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs= {'class' : 'large-input'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'large-input'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'large-input'}))
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs= {'class' : 'large-input'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'large-input'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']