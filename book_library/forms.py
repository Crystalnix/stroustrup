from urllib2 import urlopen
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import PrependedText, InlineField
from book_library.models import Book, Book_Tag, Author, Book_Request, Book_Comment, Book_Rating
from book_library.parsers import book_shop_factory


class NameField(forms.CharField):

    def to_python(self, value):
        if value:
            value = value.split(',')
            value = [tuple(x.split(None, 2)) for x in value if len(tuple(x.split())) > 1]
        return value

    def validate(self, value):
        if not value:
            raise ValidationError(["Enter first name and last name with namespace. "
                                   "Every author should be separated by comma from another author. "
                                   "Probably you wrote single (last or first) name."])


class TagField(forms.CharField):

    def to_python(self, value):
        if value:
            value = value.split(',')
        return value


class BookForm(ModelForm):
    authors_names = NameField(max_length=100, label="Add authors full names (to separate use a comma):")
    tag_field = TagField(max_length=50, label='Add tags (to separate use a comma):', required=False)
    e_version_exists = forms.BooleanField(label='E-version', required=False)
    paperback_version_exists = forms.BooleanField(label='Paper version', required=False)

    helper = FormHelper()
    helper.form_class = 'form-group'
    helper.layout = Layout(PrependedText('isbn', '13 digits'),
                           Field('title', css_class='form-control'),
                           Field('e_version_exists', css_class='form-group'),
                           Field('paperback_version_exists', css_class='form-group'),
                           Field('description', rows="3", css_class='form-control'),
                           Field('picture', css_class='form-control'),
                           Field('book_file', css_class='form-control'),
                           Field('authors_names', css_class='form-control'),
                           Field('tag_field', css_class='form-group'),
                           Submit('save_changes', 'Save', css_class='btn btn-lg btn-block btn-success form-group'))

    def clean_isbn(self):
        data = self.cleaned_data['isbn']
        if data == '':
            return data
        try:
            Book.books.get(isbn=data)
        except Book.DoesNotExist:
            return data
        raise forms.ValidationError('This ISBN is already taken.')

    def clean(self):
        cleaned_data = self.cleaned_data
        e_version_exists = self.cleaned_data['e_version_exists']
        if 'book_file' in cleaned_data:
            file_book = cleaned_data['book_file']
        else:
            return cleaned_data
        if e_version_exists and (file_book is None):
            msg = 'You selected "E-version" but did not select a file.'
            self._errors['book_file'] = self.error_class([msg])
            del cleaned_data['book_file']
        if e_version_exists is False and (file_book is not None):
            msg = 'You selected a file but did not select "E-version".'
            self._errors['book_file'] = self.error_class([msg])
            del cleaned_data['book_file']
        return cleaned_data

    class Meta:
        model = Book
        exclude = ['busy', 'users', 'authors', 'tags', 'book_rating', 'comments']

    def save(self, commit=True):
        authors = self.cleaned_data['authors_names']
        tags = self.cleaned_data['tag_field']
        book = super(BookForm, self).save(commit)
        book.authors.clear()
        book.tags.clear()
        for author in authors:
        # all inputs checks to belong to db
        # if such input not exists then it creates
        # otherwise - it just becomes book's one
            fname = author[0]
            lname = author[1]
            new_author = None
            flag = False
            for _author in Author.authors.all():
                if _author.first_name == fname and _author.last_name == lname:
                    new_author = _author
                    flag = True
                    break
            if not flag:
                new_author, created = Author.authors.get_or_create(first_name=author[0], last_name=author[1])
            book.authors.add(new_author)
        for _tag in tags:
        #as same as authors
            new_tag = None
            flag = False
            for el in Book_Tag.tags.all():
                if el.tag == _tag:
                    flag = True
                    new_tag = el
                    break
            if not flag:
                new_tag, created = Book_Tag.tags.get_or_create(tag=_tag)
            book.tags.add(new_tag)

        return book


class Book_TagForm(ModelForm):

    class Meta:
        model = Book_Tag


class AuthorForm(ModelForm):

    class Meta:
        model = Author


class SureForm(forms.Form):
    confirm = forms.BooleanField(label='Are you sure?', required=False)


class SearchForm(forms.Form):
    busy = forms.BooleanField(label='Busy', required=False)
    free = forms.BooleanField(label='Free', required=False)
    keywords = forms.CharField(label='Search', max_length=45)

    helper = FormHelper()
    helper.form_method = 'get'
    helper.form_class = "form-inline"
    helper.form_id = "search_form"
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.form_show_labels = False
    helper.layout = Layout(InlineField('busy', css_class="search_box"),
                           InlineField('free', css_class="search_box"),
                           InlineField('keywords', wrapper_class="col-xs-5"),
                           Submit('search', 'Search', css_class="btn btn-default"))


class Book_UpdateForm(BookForm):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('initial', {})['authors'] = ''
            super(BookForm, self).__init__(*args, **kwargs)
            if not self.is_bound and self.instance.pk:
                queryset_authors = self.instance.authors.all()
                authors = u", ".join(unicode(v) for v in queryset_authors)
                self.fields['authors_names'].initial = authors
                queryset_tags = self.instance.tags.all()
                tags = u",".join(unicode(v) for v in queryset_tags)
                self.fields['tag_field'].initial = tags

        def clean_isbn(self):
            data = self.cleaned_data['isbn']
            if data == '' or self.instance.isbn == data:
                return data
            try:
                Book.books.get(isbn=data)
            except Book.DoesNotExist:
                return data
            else:
                raise forms.ValidationError('This ISBN is already taken.')


class Book_RequestForm(ModelForm): #SpaT_edition
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Paste URL here'}))
    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = "form-group row"
    helper.form_show_labels = False
    helper.error_text_inline = True
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.layout = Layout(Field('title', wrapper_class="col-xs-5"),
                           Field('url', wrapper_class="col-xs-5"),
                           Submit('send', 'Send!', css_class="btn  btn-success col-md-2"))

    class Meta:
        model = Book_Request
        fields = ['title', 'url']

    def clean_url(self):
        try:
            urlopen_object = urlopen(self.cleaned_data['url'])
        except:
            raise forms.ValidationError('This URL is unavailable.')
        parser = book_shop_factory(urlopen_object.url)
        if parser is None:
            raise forms.ValidationError('This URL is incorrect. Use only the Amazon site and Ozon site.')
        else:
            self.product = parser.parse(urlopen_object)
            return self.cleaned_data['url']

    def save(self, commit=True):
        url = self.cleaned_data['url']
        title = self.cleaned_data['title']
        start_str_http = 'http'
        start_str_https = 'https'
        if not url.startswith(start_str_http) and not url.startswith(start_str_https):
            url = '//'+url
        if self.product is not None:
            Book_Request.requests.create(url=url, title=title, user=self.instance.author,
                                         book_image_url=self.product['book_image_url'],
                                         book_title=self.product['title'], book_authors=self.product['authors'],
                                         book_price=self.product['price'], book_description=self.product['description'])
        else:
            Book_Request.requests.create(url=url, title=title, user=self.instance.author)


class Book_RatingForm(ModelForm):

    class Meta:
        model = Book_Rating


class Book_CommentForm(ModelForm):
    comment = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Book_Comment
        fields = ['comment']

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = "form-group"
    helper.form_show_labels = False
    helper.error_text_inline = True
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.layout = Layout(Field('comment', rows="4", css_class='form-control'),
                           Submit('send', 'Send!', css_class="btn  btn-success"))


class PrintQRcodesForm(forms.Form):
    books = forms.ModelMultipleChoiceField(queryset=Book.books.all(), widget=forms.CheckboxSelectMultiple)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = "form-group"
    helper.form_show_labels = False
    helper.error_text_inline = True
    helper.layout = Layout(Field('books', wrapper_class="form-group"),
                           Submit('print', 'Print!', css_class="btn btn-lg btn-block btn-success form-group"))

