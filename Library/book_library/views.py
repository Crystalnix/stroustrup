from django.http import HttpResponseRedirect, HttpResponse
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
from django.core.paginator import Paginator
from os import environ
from main import settings
import datetime
import json
import math

from forms import *
from models import *

BOOKS_ON_PAGE = 5


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


class BookView(LoginRequiredView, DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data()
        if context['book'].busy:
            context['book_user'] = context['book'].client_story_record_set.latest('book_taken').user
        return context


class TagView(LoginRequiredView, DetailView):
    model = Book_Tag


class AuthorView(LoginRequiredView, DetailView):
    model = Author


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

class DeleteAuthor(Delete):
    model = Author


@login_required
def take_book_view(request, number, *args, **kwargs):
    book = Book.books.get(id=number)
    if not book.busy:
        client = request.user
        book.take_by(client)
        book.save()
        return HttpResponse(content=json.dumps({'message': 'Book taken'}))
    return HttpResponseRedirect(reverse('book:list'))


@login_required
def return_book_view(request, number, *args, **kwargs):
    book = Book.books.get(id=number)
    client = request.user
    books = client.get_users_books()
    if book.busy and books and book in books:
        book.return_by(client)
        book.save()
        return HttpResponse(content= json.dumps({'message': 'Book returned'}))
    return  HttpResponseRedirect(reverse('book:list'))


class BookListView(LoginRequiredView, ListView):
    busy = None
    free = None
    form_class = SearchForm
    page = 1

    def get_queryset(self):
        self.queryset = Book.books.all()
        if self.kwargs['slug']:
            self.busy = self.kwargs['slug'] == "busy"
        else:
            if 'busy' in self.request.GET:
                if self.request.GET['busy'] == '2':
                    self.busy = True
                else:
                    if self.request.GET['busy'] == '1':
                        self.busy = False
        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = Q()
            if form.cleaned_data['keywords']:
                keywords = form['keywords']
                keywords = list(set(keywords.data.split(' ')))  #deleting equals
                for keyword in keywords:
                    if not Book.books.filter(isbn__iexact=keyword):
                        query = query | Q(description__icontains=keyword) | Q(title__icontains=keyword)
                        query = query | Q(authors__first_name__iexact=keyword) | Q(authors__last_name__iexact=keyword)
                        query = query | Q(tags__tag__iexact=keyword)
                    else:
                        query = Q(isbn__iexact=keyword)

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
        if self.kwargs['page']:
            self.page = int(self.kwargs['page'])
        return self.queryset

    def get_context_data(self, **kwargs):
        page = Paginator(self.queryset, BOOKS_ON_PAGE)
        if self.page in page.page_range:
            self.queryset = page.page(self.page).object_list
        else:
            self.queryset = []
        context = {'object_list': set(self.queryset), "form": self.form_class(self.request.GET), "busy": self.busy, "page": page}
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
def ask_to_return(request, number, *args, **kwargs):
    book = get_object_or_404(Book, id = number)
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
    return HttpResponseRedirect(reverse("books:list"))


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


def CommentAdd(request, number, *args): #SpaT_edition
    queryset = Book.books.all()
    number=int(number)
    book = None
    for _book in queryset:
        if number == _book.id:
            book = _book
            break
    if not book:
        raise ValueError
    message = request.REQUEST.dicts[1]['Comment']
    _user=request.user
    _time = datetime.datetime.now()
    com = Book_Comment.comments.create(user = _user, comment = message, sent_time = _time)
    book.comments.add(com)
    com.save()
    return HttpResponseRedirect('../..')


def LikeRequest(request, number, *args): #SpaT_edition
    queryset = Book_Request.requests.all()
    user=request.user
    result_vote=0
    for req in queryset:

        if req.id == int(number):
            result_vote=req.vote
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
            result_vote=req.vote
            break

    return HttpResponse(content=json.dumps({
        'status':'OK',
        'vote':result_vote,
        }, sort_keys = True))

def rating_post(request, *args, **kwargs):
    number = int(args[0])
    queryset = Book.books.all()
    book = None
    for _book in queryset:
        if number == _book.id:
            book = _book
            break
    if not book:
        raise ValueError
    _user = request.user
    _rate = request.GET['score']
    _rate = float(_rate)
    _votes = int(request.GET['votes'])
    value = None
    try:
        value = book.book_rating.all()
    except Exception:
        return HttpResponse(content=json.dumps({
            'status':'BAD_GATE',
            'score': request.GET['score'],
            'msg': 'Unexpected error',
            }, sort_keys = True))
    if (value):
        for record in value:
            if record.user_owner.id == _user.id:
                _votes-=1
                if _votes>1:
                    common = float(request.GET['val'])-record.user_rating/_votes
                else:
                    common=0
                common += _rate/_votes
                common = math.ceil(common*100)/100
                book.book_rating.remove(record)
                elem = Book_Rating.rating_manager.create(user_owner = _user, user_rating = _rate, common_rating = common, votes = _votes)
                elem.save()
                book.book_rating.add(elem)

                return HttpResponse(content=json.dumps({
                    'status':'CHANGED',
                    'score': request.GET['score'],
                    'votes': request.GET['votes'],
                    'val': common,
                    'msg': 'Your vote has been changed',
                    }, sort_keys = True))


    common = (float(request.GET['val'])*(_votes-1)+_rate)/_votes
    common = math.ceil(common*100)/100
    elem = Book_Rating.rating_manager.create(user_owner = _user, user_rating = _rate, common_rating = common, votes = _votes)
    elem.save()
    book.book_rating.add(elem)
    return HttpResponse(content=json.dumps({
        'status':'OK',
        'score': request.GET['score'],
        'votes': request.GET['votes'],
        'val': common,
        'msg': 'Your vote has been approved',
        }, sort_keys = True))