from django.conf.urls import patterns, url
from book_library.views import *

urlpatterns = patterns('',
                       url(r'^page/(?P<page>\d+)?/?(?P<slug>[free|busy])?/?$',
                           BookListView.as_view(template_name='book_list.html'),
                           name='list'),

                       url(r'add/$',
                           BookAdd.as_view(success_url="/", template_name="add_book.html"),
                           name='add'),

                       url(r'^authors/(?P<pk>\d+)/$',
                           AuthorView.as_view(model=Author, template_name="author.html"),
                           name='author'),

                       url(r'^tags/(?P<pk>\d+)/$',
                           TagView.as_view(model=Book_Tag, template_name="tag.html"),
                           name='tag'),

                       url(r'^(?P<pk>\d+)/$',
                           BookView.as_view(template_name="book.html"),
                           name='book'),

                       url(r'^(?P<pk>\d+)/change/$',
                           BookUpdate.as_view(success_url="/", template_name="change_book.html"),
                           name='change'),

                       url(r'^(?P<pk>\d+)/delete/$',
                           DeleteBook.as_view(success_url="/", template_name="book_confirm_delete.html"),
                           name='delete'),

                       url(r'/take/(\d+)', take_book_view, name='take'),

                       url(r'/return/(\d+)', return_book_view, name='return'),

                       url(r'^(?P<pk>\d+)/story/$',
                           BookStoryListView.as_view(template_name='book_story.html'),
                           name='story'),

                       url(r'^(?P<pk>\d+)/ask_to_return/(\d+)$', ask_to_return,
                           name='ask'),

                       url(r'^request/(?P<page>\d+)?/?$',
                           requestBook.as_view(success_url='//', template_name='request_new.html'),
                           name='request'),

                       url(r'like/(\d+)/$',
                           LikeRequest,
                           name='like'),

                       url(r'^users/(?P<page>\d+)?/?$',
                           UsersView.as_view(template_name='users_list.html'),
                           name = 'users'),

                       url(r'rating/(\d+)',
                           rating_post,
                           name='rating'),

                       url(r'print/$',
                           PrintQrCodesView.as_view(template_name="print_qr.html"),
                           name='print'),
                       url(r'^library/$',
                           'book_library.views.library_change',
                           name='library_change'),
                       url(r'^library/(?P<pk>\d+)/delete/$',
                           DeleteUserFromLibrary.as_view(template_name="delete_user_from_library.html"),
                           name='delete_user'),

                       url(r'^library/(?P<pk>\d+)/permissions/$',
                           'book_library.views.add_permissions_for_user',
                           name='permissions_user')

                       )