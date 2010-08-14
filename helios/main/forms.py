from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
attrs_dict = { 'class': 'required' }

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should either preserve the base ``save()`` or implement
    a ``save()`` which accepts the ``profile_callback`` keyword
    argument and passes it through to
    ``RegistrationProfile.objects.create_inactive_user()``.

    """
    email = forms.EmailField(widget=forms.TextInput(
        attrs=dict(attrs_dict,maxlength=75)),
        label=u'email address')

    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=u'password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=u'password (again)')

    def clean_email(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        except MultipleObjectsReturned:
            pass
        raise forms.ValidationError(u'That email is already taken. Please choose another.')
    

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(u'You must type the same password each time')
        return self.cleaned_data