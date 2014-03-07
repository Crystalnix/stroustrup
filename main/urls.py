from django.conf.urls import patterns, include, url
from django.contrib import admin
from django_openid_auth.views import login_complete
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView
import views
from django.conf import settings
from profile.registration_app.forms import CustomAuthForm
from profile.registration_app.views import *


import warnings
warnings.simplefilter('error', DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT},
                           name='media'),
                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^$',
                           views.main_view,
                           name='mainpage'),

                       url(r'^openid/login/$',
                           'django_openid_auth.views.login_begin',
                           name='openid-login'),

                       url(r'^openid/login-complete/$',
                           login_complete,
                           name='openid-complete'),

                       url(r'^profile/',
                           include('profile.urls', namespace="profile")),

                       url(r'^invite/',
                           include('invitation.urls', namespace="invite")),

                       url(r'^landing_page/$', LandingPage.as_view(template_name='landing_page.html'), name='landing_page'),

                       url(r'^thanks/$', TemplateView.as_view(template_name='thanks.html'), name='thanks'),

                       url(r'^accounts/', include('profile.registration_app.urls')),

                       url(r'^books/', include('book_library.urls', namespace='books')),

                       url(r'^auth/login/$',
                           'django.contrib.auth.views.login',
                           {'template_name': 'registration/login.html', 'authentication_form': CustomAuthForm},
                           name='auth_login'),

                       url(r'^auth/', include('registration.auth_urls', namespace="authorisation")),

                       )

urlpatterns += staticfiles_urlpatterns()