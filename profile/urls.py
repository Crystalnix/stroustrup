from django.conf.urls import patterns, url
from django.contrib import admin

from profile.views import *


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ProfileView.as_view(template_name="profile.html",
                                                     )
        ,name='profile'),
    url(r'^change/$', 'profile.views.profile_change',
        name='change'),
    url(r'^users/$', UsersView.as_view(template_name='users_list.html',),
        name='all'),
    url(r'^library/$')
    )