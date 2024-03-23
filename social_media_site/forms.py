from django import forms
from django.contrib.auth.models import User
from .models import Post

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
    birthdate = forms.DateField(label="Date of Birth",
                                required=False,
                                widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                                input_formats=["%Y-%m-%d"])
    profile_photo = forms.ImageField(label="Profile photo", required=False)
    cover_photo = forms.ImageField(label="Cover photo", required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]

        if (User.objects.filter(username=username).exists()):
            raise forms.ValidationError("Username already used")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if (User.objects.filter(email=email).exists()):
            raise forms.ValidationError("Email already used")

        return email

    def clean_password2(self):
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]

        if (password != password2):
            raise forms.ValidationError("Passwords don't match")

        return password2


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "photo"]
        widgets = {
            'text': forms.Textarea(attrs={
                'id': 'post_text',
                'required': True,
                'placeholder': 'Write your post...'
                }
            ),

            'photo': forms.FileInput(attrs={
                'id': 'post_photo',
                'required': False
                }
            ),
        }





