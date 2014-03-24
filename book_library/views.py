import json
import math
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.core import mail
from django.shortcuts import get_object_or_404, Http404
from django.db.models import Q
from pure_pagination.mixins import PaginationMixin
from main.settings import BOOKS_ON_PAGE, REQUEST_ON_PAGE, USERS_ON_PAGE, EMAIL_HOST_USER
from book_library.forms import *
from book_library.models import *
from profile.models import User
from django_xhtml2pdf.utils import generate_pdf
from urllib2 import urlopen
from urlparse import urlparse
from amazon.api import AmazonAPI
from re import search
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect

class StaffOnlyView(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, request, *args, **kwargs):
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


class ManagerOnlyView(object):
    @method_decorator(user_passes_test(lambda u:  u.is_active and u.is_manager))
    def dispatch(self, request, *args, **kwargs):
        return super(ManagerOnlyView, self).dispatch(request, *args, **kwargs)


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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library:
            return HttpResponseRedirect(reverse('books:list'))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

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


class BookAdd(ManagerOnlyView, FormView):
    form_class = BookForm
    object = None

    def form_valid(self, form):
        form.save(self.request.user.library)
        return HttpResponseRedirect(reverse("books:list"))


class BookUpdate(ManagerOnlyView, UpdateView):
    model = Book
    form_class = Book_UpdateForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library:
            return HttpResponseRedirect(reverse('books:list'))
        return super(BookUpdate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library:
            return HttpResponseRedirect(reverse('books:list'))
        return super(BookUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user.library)
        return HttpResponseRedirect(reverse("books:list"))


class DeleteBook(ManagerOnlyView, DeleteView):
    model = Book

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library:
            return HttpResponseRedirect(reverse('books:list'))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library:
            return HttpResponseRedirect(reverse('books:list'))
        return self.delete(request, *args, **kwargs)

@login_required
def take_book_view(request, number, *args, **kwargs):
    book = Book.books.get(id=number)
    if not book.busy:
        client = request.user
        book.take_by(client)
        book.save()
        return HttpResponse(content=json.dumps({'message': 'Book taken'}))
    return HttpResponseRedirect(reverse('books:list'))


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
        self.queryset = Book.books.filter(library=self.request.user.library)
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
                self.queryset = Book.books.filter(query, library=self.request.user.library).distinct()
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

    def get_queryset(self):
        self.queryset = User.objects.filter(library=self.request.user.library)



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

    def get_context_data(self, **kwargs):
        context = {}
        context['object_list'] = self.queryset
        context['form'] = self.get_form(self.form_class)
        return super(requestBook, self).get_context_data(**context)

    def form_valid(self, form):
            url = form.data['url']
            title = form.data['title']
            start_str_http = 'http'
            start_str_https = 'https'
            if not url.startswith(start_str_http) and not url.startswith(start_str_https):
                url = start_str_http+'://'+url
            product_url = search('https?://www.amazon.[a-z]+\/[A-Za-z0-9-!$@&?%\(\)]+\/dp/([0-9A-Z]+)', url)
            if product_url is not None:
                    id_product = product_url.group(1)
                    amazon = AmazonAPI(settings.AMAZON_ACCESS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_ASSOC_TAG)
                    product = amazon.lookup(ItemId=id_product)
                    authors = u", ".join(unicode(v) for v in product.authors)
                    price = '{0} {1}'.format(product.price_and_currency[0], product.price_and_currency[1])
                    Book_Request.requests.create(url=url, title=title, user=self.request.user,
                                                 book_image_url=product.medium_image_url,
                                                 book_title=product.title, book_authors=authors,
                                                 book_price=price)
                    return HttpResponseRedirect(reverse("books:request"))
            else:
                Book_Request.requests.create(url=url, title=title, user=self.request.user)
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
        'status': 'OK',
        'score': request.GET['score'],
        'votes': request.GET['votes'],
        'val': common,
        'msg': 'Your vote has been approved',
        }, sort_keys=True))


class PrintQrCodesView(ManagerOnlyView, FormView):
    form_class = PrintQRcodesForm

    def get(self, request, *args, **kwargs):
        library = self.request.user.library
        form = self.form_class(library)
        queryset = form.fields['books'].queryset
        return self.render_to_response(self.get_context_data(form=form, queryset=queryset))

    def form_valid(self, form):
        data = form.cleaned_data['books']
        context = {'books': data}
        resp = HttpResponse(content_type='application/pdf')
        result = generate_pdf('book_card.html', file_object=resp, context=context)
        return result


@csrf_protect
@login_required
def library_change(request):
    template_name = 'library_change.html'
    profile_change_form = LibraryForm
    post_change_redirect = reverse("profile:profile", args=str(request.user.pk))
    if request.user.is_manager:
        if request.method == "POST":
            form = profile_change_form(library=request.user.library, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_change_redirect)
        form = profile_change_form(library=request.user.library)
        context = {'form': form}
        return TemplateResponse(request, template_name, context)
    else:
        return HttpResponseRedirect(post_change_redirect)


class DeleteUserFromLibrary(ManagerOnlyView, DeleteView):
    model = User

    def get_success_url(self):
        return reverse("books:users")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library or not self.request.user.is_manager:
            return HttpResponseRedirect(reverse('books:users'))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.library != self.request.user.library or not self.request.user.is_manager:
            return HttpResponseRedirect(reverse('books:users'))
        return self.delete(request, *args, **kwargs)


def add_permissions_for_user(request, **kwargs):
    try:
        user = User.objects.get(pk=int(kwargs['pk']))
    except User.DoesNotExist:
        raise Http404
    if request.user.is_manager and user.library == request.user.library:
        if user.is_manager:
            user.is_manager = False
            user.save()
        else:
            user.is_manager = True
            user.save()
    return HttpResponseRedirect(reverse("profile:profile", args=kwargs['pk']))
