__author__ = 'romanusynin'
from django.db import models
from book_library.models import Library


class Invite(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=75, blank=True)
    last_name = models.CharField(max_length=75, blank=True)
    code = models.CharField(max_length=50)
    is_sent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    who_invite = models.ForeignKey(Library, verbose_name='Library', blank=True, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    date_used = models.DateTimeField(auto_now_add=True)

