__author__ = 'romanusynin'
from django.conf.urls import patterns, url
from invitation.views import InviteAdd


urlpatterns = patterns('',
                       url(r'^send/$',
                           InviteAdd.as_view(),
                           name='send'),

                       url(r'^send/success/$',
                           "invitation.views.success_sent_invite",
                           name='success_sent'),

                       url(r'^activate/(?P<code>\w+)',
                           'invitation.views.activate_invite',
                           name='activate')
                       )

