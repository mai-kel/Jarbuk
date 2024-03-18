from django import forms
from django.conf import settings


class UserForm(forms.Form):
    first_name = forms.CharField(label="First name", max_length=30, required=False)
    last_name = forms.CharField(label="Last name", max_length=30, required=False)

    def clean(self):
        cd = self.cleaned_data

        first_name = cd["first_name"]
        last_name = cd["last_name"]

        if (not (first_name or last_name)):
            raise forms.ValidationError("At least one field must be filled")

        return cd



class RegistrationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30, required=True)
    first_name = forms.CharField(label="First name", max_length=30, required=True)
    last_name = forms.CharField(label="Last name", max_length=30, required=True)
    email = forms.EmailField(label="Email", max_length=50, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput, required=True)
    birthdate = forms.DateField(label="Birth date", required=False)
    profile_photo = forms.ImageField(label="Profile photo")
    cover_photo = forms.ImageField(label="Profile photo")

    def clean_username(self):
        username = self.cleaned_data["username"]

        if (settings.AUTH_USER_MODEL.objects.filter(username=username).exists()):
            raise forms.ValidationError("Username already used")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if (settings.AUTH_USER_MODEL.objects.filter(email=email).exists()):
            raise forms.ValidationError("Email already used")

        return email

    def clean_password2(self):
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]

        if (password != password2):
            raise forms.ValidationError("Passwords don't match")

        return password2




