from urllib2 import urlopen
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import PrependedText, InlineField, FormActions
from book_library.models import Book, Book_Tag, Author, Book_Request, Book_Comment, Book_Rating, Library

from invitation.models import Invite


class InviteForm(ModelForm): #SpaT_edition

    helper = FormHelper()
    helper.form_class = 'form-signin'
    helper.form_show_labels = False
    helper.layout = Layout(Field('email'),
                           Field('first_name'),
                           Field('last_name'),
                           FormActions(Submit('save_changes_profile', 'Save', css_class='btn-lg btn-block btn-success')))

    class Meta:
        model = Invite
        fields = ['email', 'first_name', 'last_name']
        widgets = {'email': forms.TextInput(attrs={'placeholder': 'E-mail'}),
                   'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
                   'last_name': forms.TextInput(attrs={'placeholder': 'Last name'})
                   }
