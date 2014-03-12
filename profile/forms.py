from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions
from profile.models import Library, User
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class ProfileForm(ModelForm):
    avatar = forms.ImageField(widget=forms.ClearableFileInput(attrs={'placeholder': 'Avatar'}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
                   'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
                   'email': forms.TextInput(attrs={'placeholder': 'E-mail'})}

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_show_labels = False
    helper.layout = Layout(Field('first_name'),
                           Field('last_name'),
                           Field('email'),
                           Field('avatar', wrapper_class='form-control'),
                           FormActions(Submit('save_changes_profile', 'Save', css_class='btn-lg btn-block btn-success')))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email
        if not self.is_bound and self.user.pk:
            profile = self.user.get_profile()
            self.fields['avatar'].initial = profile.avatar

    def save(self, commit=True):
        profile = self.user
        profile.first_name = self.cleaned_data['first_name']
        profile.last_name = self.cleaned_data['last_name']
        profile.email = self.cleaned_data['email']
        profile.save()
        photo = self.cleaned_data['avatar']
        if photo is None:
            return profile
        if photo is False:
            profile.get_profile().avatar.delete()
            photo = None
        profile.get_profile().avatar = photo
        new_avatar = profile.get_profile()
        new_avatar.save()
        return profile



