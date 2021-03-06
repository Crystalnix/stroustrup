# -*- coding: utf-8 -*-
import json
import math
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import DetailView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import mail
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from pure_pagination.mixins import PaginationMixin
from main.settings import BOOKS_ON_PAGE, REQUEST_ON_PAGE, USERS_ON_PAGE, EMAIL_HOST_USER
from book_library.forms import *
from book_library.models import *
from django_xhtml2pdf.utils import generate_pdf
from amazon.api import AmazonAPI
from re import search
from django.db.models.signals import post_delete
from urlparse import urlparse
from parsers import book_shop_factory


class StaffOnlyView(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, request, *args, **kwargs):
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


class LoginRequiredView(object):
    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)


class AddRequestView(CreateView): #SpaT_edition
    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(AddRequestView, self).dispatch(request, *args, **kwargs)


class BookView(LoginRequiredView, DetailView, FormView):
    model = Book
    form_class = Book_CommentForm
    object = None

    def get_context_data(self, **kwargs):
        context = {}
        context['book'] = self.get_object()
        if context['book'].busy:
            context['book_user'] = context['book'].taken_by
        context['form'] = self.get_form(self.form_class)
        return super(BookView, self).get_context_data(**context)

    def form_valid(self, form):
        book = self.get_object()
        msg = form.cleaned_data['comment']
        user = self.request.user
        comment = Book_Comment.comments.create(user=user, comment=msg)
        book.comments.add(comment)
        return HttpResponseRedirect(reverse("books:book", args=[book.id]))


class TagView(LoginRequiredView, DetailView):
    model = Book_Tag


class AuthorView(LoginRequiredView, DetailView):
    model = Author


class BookAdd(StaffOnlyView, CreateView):
    model = Book
    form_class = BookForm
    object = None


class BookUpdate(StaffOnlyView, UpdateView):
    model = Book
    form_class = Book_UpdateForm


class DeleteBook(StaffOnlyView, DeleteView):
    model = Book


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
        return HttpResponse(content=json.dumps({'message': 'Book returned'}))
    return HttpResponseRedirect(reverse('book:list'))


class BookListView(PaginationMixin, LoginRequiredView, ListView):
    busy = None
    free = None
    form_class = SearchForm
    page = 1
    paginate_by = BOOKS_ON_PAGE

    def get_queryset(self):
        self.queryset = Book.books.all()
        try:
            self.busy = self.request.GET['busy']
        except KeyError:
            self.busy = False

        try:
            self.free = self.request.GET['free']
        except KeyError:
            self.free = False
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



            if self.busy and not self.free:
                query = query & Q(busy=True)
            if not self.busy and self.free:
                query = query & Q(busy=False)

            if query:
                self.queryset = Book.books.filter(query).distinct()
        if self.kwargs['page']:
            self.page = int(self.kwargs['page'])

        return self.queryset

    def get_context_data(self, **kwargs):
        context = {}
        context['object_list'] = self.queryset
        context['form'] = self.form_class(self.request.GET)
        context['busy'] = self.busy
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
def ask_to_return(request, *args, **kwargs):
    book = get_object_or_404(Book, id=request.GET['ID'])
    if book.busy:
        profile = book.taken_by()
        if request.user != profile:
            if request.user.is_staff:
                authors = u", ".join(unicode(v) for v in book.authors.all())
                server_email = EMAIL_HOST_USER
                email = mail.EmailMessage('Book return request', "Manager {0} ({1} {2}) is asking you to return "
                                                                 "the book: ''{3}'' author(s): {4}."
                                                                 " You can return it by click on this link: {5}{6}"
                                                                 .format(request.user.username, request.user.first_name,
                                                                         request.user.last_name, book.title,
                                                                         authors, settings.DOMAIN,
                                                                         reverse('books:book', kwargs={'pk': book.id})),
                                          server_email, [profile.email])
                email.send()
            else:
                Request_Return.objects.create(book=book, user_request=request.user)
            return HttpResponse(content=json.dumps({'message': 'Request has been sent'}))
    return HttpResponseRedirect(reverse("books:list"))


class UsersView(PaginationMixin, LoginRequiredView, ListView):
    model = User
    page = 1
    paginate_by = USERS_ON_PAGE
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        return super(UsersView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        context['object_list']=self.queryset
        return super(UsersView, self).get_context_data(**context)


class requestBook(PaginationMixin, AddRequestView, ListView): #SpaT_edition
    model = Book_Request
    form_class = Book_RequestForm
    object = None
    object_list = None
    queryset = Book_Request.requests.order_by('-id')
    page = 1
    paginate_by = REQUEST_ON_PAGE
    success_url = reverse_lazy("books:request")

    def get_context_data(self, **kwargs):
        context = {}
        context['object_list'] = self.queryset
        context['form'] = self.get_form(self.form_class)
        return super(requestBook, self).get_context_data(**context)

    def form_valid(self, form):
            form.instance.author = self.request.user
            self.object = form.save()
            return HttpResponseRedirect(reverse("books:request"))


def LikeRequest(request, number, *args): #SpaT_edition
    queryset = Book_Request.requests.all()
    user = request.user
    result_vote = 0
    all_users = []
    for req in queryset:

        if req.id == int(number):

            result_vote = req.vote
            flag = True
            for user1 in req.users.all():
                if user1.id == user.id:
                    flag = False
                    break
            if not flag:
                req.vote -= 1

                result_vote = req.vote
                req.users.remove(user)
                req.save()

                for i in req.users.all():
                    all_users.append(i.username)

                break

            req.vote += 1
            req.users.add(user)
            req.save()
            for i in req.users.all():
                    all_users.append(i.username)
            result_vote = req.vote
            break

    return HttpResponse(content=json.dumps({
        'status': 'OK',
        'vote': result_vote,
        'listuser': all_users,

        }, sort_keys=True))

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
            'status': 'BAD_GATE',
            'score': request.GET['score'],
            'msg': 'Unexpected error'},
            sort_keys=True))
    if value:
        for record in value:
            if record.user_owner.id == _user.id:
                _votes -= 1
                if _votes > 1:
                    common = float(request.GET['val'])-record.user_rating/_votes
                else:
                    common = 0
                common += _rate/_votes
                common = math.ceil(common*100)/100
                book.book_rating.remove(record)
                elem = Book_Rating.rating_manager.create(user_owner=_user, user_rating=_rate, common_rating=common, votes=_votes)
                book.book_rating.add(elem)

                return HttpResponse(content=json.dumps({'status': 'CHANGED',
                                                        'score': request.GET['score'],
                                                        'votes': request.GET['votes'],
                                                        'val': common,
                                                        'msg': 'Your vote has been changed'},
                    sort_keys=True))
    common = (float(request.GET['val'])*(_votes-1)+_rate)/_votes
    common = math.ceil(common*100)/100
    elem = Book_Rating.rating_manager.create(user_owner=_user, user_rating=_rate, common_rating=common, votes=_votes)
    elem.save()
    book.book_rating.add(elem)
    return HttpResponse(content=json.dumps({
        'status':'OK',
        'score': request.GET['score'],
        'votes': request.GET['votes'],
        'val': common,
        'msg': 'Your vote has been approved',
        }, sort_keys=True))


class PrintQrCodesView(LoginRequiredView, FormView):
    form_class = PrintQRcodesForm
    template_name = "print_qr.html"

    def form_valid(self, form):
        data = form.cleaned_data['books']
        context = {'books': data}
        resp = HttpResponse(content_type='application/pdf')
        result = generate_pdf('book_card.html', file_object=resp, context=context)
        return result


class RequestBookSave(BookAdd):
    success_url = '/'
    template_name = 'add_book.html'

    def get_initial(self):
        initial = super(RequestBookSave, self).get_initial()
        initial = initial.copy()
        try:
            book = Book_Request.requests.get(pk=self.kwargs['pk'])
            initial['title'] = book.book_title
            initial['description'] = book.book_description
            initial['authors_names'] = book.book_authors
            return initial
        except Book_Request.DoesNotExist:
            return initial

    def form_valid(self, form):
        book = Book_Request.requests.get(pk=self.kwargs['pk'])
        book.delete()
        return super(RequestBookSave, self).form_valid(form)
