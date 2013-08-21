from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core import mail
from django.contrib.sites.models import RequestSite
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
import settings

from forms import *
from models import *


class StaffOnlyView(object):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, request, *args, **kwargs):
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


class LoginRequiredView(object):

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)


class BookFormView(StaffOnlyView, FormView):
    form_class = BookForm

    def get(self, request, *args, **kwargs):
        return super(BookFormView, self).get(self, request, *args, **kwargs)


class BookView(DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data()
        if context['book'].busy:
            context['book_user'] = context['book'].client_story_record_set.latest('book_taken').user
        return context


class AddView(StaffOnlyView, CreateView):

    def get(self, request, *args, **kwargs):
        return super(AddView, self).get(self, request, *args, **kwargs)


class AuthorAdd(AddView):
    model = Author
    form_class = AuthorForm


class TagAdd(AddView):
    model = Book_Tag
    form_class = Book_TagForm


class BookAdd(AddView):
    model = Book
    form_class = BookForm
    object = None


class BookUpdate(StaffOnlyView, UpdateView):
    model = Book
    form_class = BookForm

    def get(self, request, *args, **kwargs):
        return super(BookUpdate, self).get(self, request, *args, **kwargs)


class Delete(StaffOnlyView, DeleteView):

    def get(self, request, *args, **kwargs):
        return super(Delete, self).get(self, request, *args, **kwargs)


class DeleteBook(Delete):
    model = Book


class DeleteTag(Delete):
    model = Book_Tag


class DeleteAuthor(Delete):
    model = Author

@dajaxice_register()
@login_required
def take_book_view(request, **kwargs):
    book = Book.books.get(id=kwargs['pk'])
    if not book.busy:
        client = request.user
        book.take_by(client)
        book.save()
        if request.is_ajax():
            return simplejson.dumps({'message': 'Book taken'})
    return HttpResponseRedirect(reverse('mainpage'))

@dajaxice_register
@login_required
def return_book_view(request, **kwargs):
    book = Book.books.get(id=kwargs['pk'])
    client = request.user
    books = client.get_users_books()
    if book.busy and books and book in books:
        book.return_by(client)
        book.save()
        if request.is_ajax():
            return simplejson.dumps({'message': 'Book returned'})
    return HttpResponseRedirect(reverse('mainpage'))


class BookListView(LoginRequiredView, ListView):
    busy = None
    free = None
    form_class = SearchForm

    def get_queryset(self):
        self.queryset = Book.books.all()

        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = Q()
            if form.cleaned_data['keywords']:
                keywords = form['keywords']
                keywords = list(set(keywords.data.split(' ')))  #deleting equals
                for keyword in keywords:
                    query = Q(isbn__iexact=keyword)
                    if not Book.books.filter(query):
                        query = Q(description__icontains=keyword) | Q(title__icontains=keyword)
                        query = query | Q(authors__first_name__iexact=keyword) | Q(authors__last_name__iexact=keyword)
                        query = query | Q(tags__tag__iexact=keyword)

            try:
                self.busy = form['busy'].data
            except KeyError:
                self.busy = False
            try:
                self.free = form['free'].data
            except KeyError:
                self.free = False
            if self.busy != self.free:
                if self.busy:
                    query = query | Q(busy=True)
                else:
                    query = query | Q(busy=False)
            if query:
                self.queryset = Book.books.filter(query)


        return self.queryset

    def get_context_data(self, **kwargs):
        context = {'object_list': set(self.queryset), "form": self.form_class(self.request.GET), "busy": self.busy}
        return super(BookListView, self).get_context_data(**context)


class BookStoryListView(LoginRequiredView, ListView):

    def get(self, request, *args, **kwargs):
        return super(BookStoryListView, self).get(request, *args, **kwargs)

    model = Client_Story_Record

    def get_context_data(self, **kwargs):
        context = {}
        pk = self.kwargs['pk']
        records_list = Client_Story_Record.records.filter(book__id=pk)
        context['object_list'] = records_list
        context['pk'] = pk
        return super(BookStoryListView, self).get_context_data(**context)

@login_required()
def ask_to_return(request, **kwargs):
    book = get_object_or_404(Book, pk=kwargs['pk'])
    if book.busy:
        profile = book.taken_by()
        if request.user != profile:
            authors_string = ""
            for author in book.authors.all():
                authors_string += author.__unicode__()
            site = RequestSite(request)
            server_email = settings.EMAIL_HOST_USER
            email = mail.EmailMessage('Book return request', "User %(username)s (%(firstname)s %(lastname)s) asks you"
                                                             " to return the book %(book)s %(author)s."
                                                             " You can return it by click on this link: %(link)s"%
                                                             {'username': request.user.username,
                                                              'firstname': request.user.first_name,
                                                              'lastname': request.user.last_name,
                                                              'book': book.__unicode__(),
                                                              'author': authors_string,
                                                              'link': "http://%(site)s/books/%(id)s/return/"
                                                                      % {'id': book.id, 'site': site.domain}
                                                             },
                                      server_email,
                                      [profile.email])
            email.send()
            return render_to_response('asked_successfully.html', {'book': book})
    return HttpResponseRedirect("books:list")


class UsersView(LoginRequiredView, ListView):
    model = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        return super(UsersView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        context['object_list']=self.queryset
        return super(UsersView, self).get_context_data(**context)

class AddRequestView(CreateView): #SpaT_edition
    @method_decorator(login_required())
    def get(self, request, *args, **kwargs):
        return super(AddRequestView, self).get(self, request, *args, **kwargs)


class requestBook(AddRequestView): #SpaT_edition
    model = Book_Request
    form_class = Book_RequestForm
    object = None
    queryset = Book_Request.requests.all()


    def get_context_data(self, **kwargs):
        context = {'requests': Book_Request.requests.all(), "form" : self.get_form(self.form_class)}
        return super(requestBook, self).get_context_data(**context)
    def post(self, request, *args, **kwargs):

        if request.POST['url'] and request.POST['title']:
            _url=request.POST['url']
            _title=request.POST['title']
            req = Book_Request.requests.create(url=_url, title=_title, user=request.user)

            req.save()
            return HttpResponseRedirect('//')
        return super(AddRequestView, self).post(request, *args, **kwargs)



def LikeRequest(request, number): #SpaT_edition
    queryset = Book_Request.requests.all()
    user=request.user
    for req in queryset:
        for user1 in req.users.all():
            print(user1,'\n')
        if req.id == int(number):

            flag = True
            for user1 in req.users.all():
                if user1.id == user.id:
                    flag=False
                    break
            if not flag:
                break
            req.vote+=1
            req.users.add(user)
            req.save()
            for user1 in req.users.all():
                print(user1,'\n')
            break

    return HttpResponseRedirect('../../request')