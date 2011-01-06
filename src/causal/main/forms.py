from django import forms
from causal.main.models import UserProfile, User

class UserProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = UserProfile
        fields = ('id', 'timezone', 'user',)

