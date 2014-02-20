from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_thumbnails.fields import ThumbnailerImageField


class Profile_addition(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='profile')
    avatar = ThumbnailerImageField(upload_to='user_avatar')


@receiver(post_save, sender=User)
def create_profile_addition(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile_addition.objects.get_or_create(user=instance)

