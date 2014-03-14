from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.db.models.signals import post_save
from django.dispatch import receiver
from book_library.views import ManagerOnlyView
from invitation.models import Invite
from invitation.forms import InviteForm
import string
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, reverse_lazy
from urlparse import urljoin
from profile.models import User
import hashlib
import uuid


def success_sent_invite(request):
    template_name = 'invitation_sent.html'
    return TemplateResponse(request, template_name)


class InviteAdd(ManagerOnlyView, CreateView):
        model = Invite
        form_class = InviteForm
        template_name = 'add_invite.html'
        success_url = reverse_lazy('invite:success_sent')

        def form_valid(self, form):
            form.instance.who_invite = self.request.user.library
            size = 50   # code.max_length
            allowed = string.ascii_letters
            randomstring = ''.join([allowed[random.randint(0, len(allowed) - 1)] \
                                    for x in xrange(size)])
            form.instance.code = randomstring
            return super(InviteAdd, self).form_valid(form)


@receiver(post_save, sender=Invite)
def send_email_invite(sender, instance, created, **kwargs):
    email = instance.email
    link = urljoin('//{}'.format(Site.objects.get_current().domain), reverse("invite:activate", kwargs={'code': instance.code}))
    context = {'library': instance.who_invite, 'link': link}
    msg = render_to_string('invite_mail.txt', context)
    send_mail('You are invited', msg, 'Stroustrup Library', [email])
    instance.is_sent = True


def activate_invite(request, **kwargs):
    success_template_name = 'activate_invite.html'
    fail_template_name = 'invite_already_activated.html'
    try:
        invite = Invite.objects.get(code=kwargs['code'])
    except Invite.DoesNotExist:
        return TemplateResponse(request, fail_template_name)
    username = uuid.uuid1()
    while User.objects.filter(username=username):
        username = username[:-1]
    pass_size = 12
    allowed = string.ascii_letters
    password = ''.join([allowed[random.randint(0, len(allowed) - 1)] \
                                    for x in xrange(pass_size)])
    user = User.objects.create_user(username, invite.email, password, first_name=invite.first_name, last_name=invite.last_name, library=invite.who_invite)
    user.save()
    invite.delete()
    email = user.email
    link = urljoin('//{}'.format(Site.objects.get_current().domain), reverse('authorisation:auth_login'))
    context = {'login': user.email, 'password': password, 'link': link}
    msg = render_to_string('login_password_mail.txt', context)
    send_mail('Your login details', msg, 'Stroustrup Library', [email])
    return TemplateResponse(request, success_template_name)