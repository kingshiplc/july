from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        domain = data.split('@')[1]
        domain_list = ["govt.lc", "gosl.gov.lc"]
        if domain not in domain_list:
            raise forms.ValidationError(
                "Please enter an Email Address with a valid domain")
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Email already exists")
        return data

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
