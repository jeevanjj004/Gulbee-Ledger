from django import forms
from django.contrib.auth.models import User
class addUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["password","first_name","last_name","email"]
