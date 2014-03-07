__author__ = 'romanusynin'
from django.conf.urls import patterns, url
from invitation.views import InviteAdd


urlpatterns = patterns('',
                       url(r'^send/$',
                           InviteAdd.as_view(),
                           name='send'),

                       url(r'^activate/(?P<code>\w+)',
                           'invitation.views.activate_invite',
                           name='activate')
                       )
