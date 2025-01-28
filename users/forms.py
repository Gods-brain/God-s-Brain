from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class UserRegisterationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True, label="Username")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if not User.objects.filter(username=username, email=email, is_active=True).exists():
            raise ValidationError("No active user found with this email and username combination.")

        return cleaned_data

    def get_users(self, email):
        username = self.cleaned_data.get("username")
        return User.objects.filter(email=email, username=username, is_active=True)


class CustomPasswordResetConfirmForm(SetPasswordForm):
    # Customization (if needed), otherwise you can use SetPasswordForm directly
    pass


