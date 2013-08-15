from django.forms import ModelForm
from models import Book, Book_Tag, Author
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import FileField
from django.forms.models import save_instance
from django.db.models import Q


class NameField(forms.CharField):

    def validate(self, value):
        strings = value.split(' ')
        if len(strings) > 1:
            fname = strings[0]
            lname = strings[1]
            filter = Q(first_name__iexact=fname) &\
                         Q(last_name__iexact=lname)
            if Author.authors.filter(filter):
                raise ValidationError(["Author already exists."])
        else:
            raise ValidationError(["Enter first name and last name with namespace."])


class BookForm(ModelForm):
    author_name = NameField(max_length=90, required=False, label="New author first name")
    authors = forms.ModelMultipleChoiceField(queryset=Author.authors.all(), required=False, label="Authors")

    class Meta:
        model = Book
        exclude = ['busy', 'users']

    def save(self, commit=True):
        if self.cleaned_data['author_name']:
            strings = self.cleaned_data['author_name'].split(' ')
            fname = strings[0]
            lname = strings[1]
            author = Author.authors.create(first_name=fname, last_name=lname)
            book = super(BookForm, self).save(commit=True)
            book.authors.add(author)
            book.save()
            return book
        else:
            return super(BookForm, self).save(commit=True)


class Book_TagForm(ModelForm):

    class Meta:
        model = Book_Tag


class AuthorForm(ModelForm):

    class Meta:
        model = Author


class SureForm(forms.Form):
    confirm = forms.BooleanField(label='Are you sure?', required=False)


class SearchForm(forms.Form):
    busy = forms.NullBooleanField(label="Busy")
    keywords = forms.CharField(label="Search", max_length=45, required=False)