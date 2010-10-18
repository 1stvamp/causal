from django import forms
from causal.main.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

