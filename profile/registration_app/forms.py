from registration.forms import RegistrationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm



class CustomRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                label=_("Username"),
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
                                widget=forms.TextInput(attrs={'placeholder': 'Username'})
                                )
    email = forms.EmailField(label=_("E-mail"),
                             widget=forms.TextInput(attrs={'placeholder': 'E-mail'})
                             )
    password1 = forms.CharField(label=_("Password"),
                                min_length=8,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
                                )
    password2 = forms.CharField(label=_("Password (again)"),
                                min_length=8,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password (again)'})
                                )
    captcha = ReCaptchaField()

    good_domains = ['crystalnix.com']

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_method = 'POST'
    helper.form_show_labels=False
    helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('password1'),
            Field('password2'),
            Field('captcha'),
            Submit('sign_up', 'Sign up!', css_class='btn btn-lg btn-block btn-success')
            )

    def clean_email(self):

        email_domain = self.cleaned_data['email'].split('@')[1]
        if not email_domain in self.good_domains:
            raise forms.ValidationError("You must use the domain crystalnix.com.")
        existing = User.objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        else:
            return self.cleaned_data['email']


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(max_length=254,
                            widget=forms.TextInput(attrs={'placeholder': 'Email'})
                            )
    password = forms.CharField(
        label=_("Password"),
        max_length=4096,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_method = 'POST'
    helper.help_text_inline = False
    helper.error_messages = True
    helper.form_show_labels = False
    helper.layout = Layout('username',
                           'password',
                           FormActions(Submit('sign_in_auth', 'Sign in!', css_class='btn btn-lg btn-block btn-primary'))
    )




class LandingForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))

    helper = FormHelper()
    helper.form_method='post'
    helper.form_class = "form-signin"
    helper.form_show_labels=False
    helper.layout = Layout(
                'email',
                 FormActions(
                                Submit('send_letter', 'Send!', css_class='btn btn-lg btn-block btn-primary'),
                           )
    )


class CustomChangePassForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Old password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password (again)'}))

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_show_labels = False
    helper.layout = Layout(
        'old_password',
        'new_password1',
        'new_password2',
        FormActions(Submit('change_pass','Change my password', css_class='btn btn-lg btn-block btn-primary'),
        )
    )
