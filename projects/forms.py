# projects/forms.py

from django import forms
from .models import Profile

class ClickUpTokenForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['clickup_token']

