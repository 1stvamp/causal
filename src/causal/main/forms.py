from django import forms
from timezones.forms import PRETTY_TIMEZONE_CHOICES
from causal.main.models import UserProfile, User

class UserProfileForm(forms.ModelForm):
    timezone_flat = forms.ChoiceField(label='Timezone', choices=PRETTY_TIMEZONE_CHOICES)
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'timezone_flat',)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Set default for timezone, as we've overriden drop-down with self.timezone_flat
        instance = kwargs.get('instance', None)
        if instance:
            self.fields['timezone_flat'].initial = instance.timezone

    def save(self, force_insert=False, force_update=False, commit=True):
        tz = self.cleaned_data['timezone_flat']
        del self.cleaned_data['timezone_flat']
        instance = super(forms.ModelForm, self).save(commit=False)
        # *sigh*, because certain ppl haven't pushed a new release for Django 1.2,
        # we'll have to monkey patch this for now
        instance._meta.fields[-1].to_python = lambda x: unicode(x)
        instance.id = self.cleaned_data['id']
        instance.timezone = tz
        print instance.pk
        instance.save()
        print instance.pk
        return instance
