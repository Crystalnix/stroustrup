from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions
from profile.models import Profile_addition
from django.core.urlresolvers import reverse

class AskReturnForm(forms.Form):
    def __init__(self, queryset, *args, **kwargs):
        super(AskReturnForm, self).__init__(*args, **kwargs)
        self.fields["choices"] = forms.ModelChoiceField(queryset=queryset, label="Select book to ask")


class ProfileForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))
    avatar = forms.ImageField(widget=forms.ClearableFileInput(attrs={'placeholder': 'Avatar'}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_show_labels = False

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if not self.is_bound and self.instance.pk:
            profile = self.instance.get_profile()
            self.fields['avatar'].initial = profile.avatar
            cancel_url = reverse('profile:profile', kwargs={'pk': self.instance.pk})
            self.helper.layout = Layout(Field('first_name'),
                                        Field('last_name'),
                                        Field('email'),
                                        Field('avatar',
                                              wrapper_class='form-control'),
                                        FormActions(Submit('save_changes_profile', 'Save',
                                                           css_class='btn btn-lg btn-success'),
                                                    Button('cancel',
                                                           'Cancel',
                                                           onclick='window.location.href="{}"'.format(cancel_url),
                                                           css_class='btn btn-lg btn-danger '),
                                        css_class='btn-group  btn-group-lg form-actions', id='id-action-form-change'))

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit)
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


class ProfileFormAddition(ModelForm):

    class Meta:
        model=Profile_addition

