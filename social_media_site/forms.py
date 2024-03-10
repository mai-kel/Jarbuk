from django import forms

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
