import datetime
from cStringIO import StringIO
# from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.contrib import auth
from easy_thumbnails.fields import ThumbnailerImageField
from django.dispatch import receiver
from django.db.models.signals import post_save
import qrcode
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import get_model

User = 'profile.CustomUser'

class Library(models.Model):
    libraries = models.Manager()

    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Client_Story_Record(models.Model):
    records = models.Manager()

    book = models.ForeignKey('Book')
    user = models.ForeignKey(User)
    book_taken = models.DateTimeField(auto_now_add=True, blank=False)
    book_returned = models.DateTimeField(null=True, blank=True)


class Author(models.Model):
    authors = models.Manager()

    first_name = models.CharField(max_length=45, verbose_name="First name")
    last_name = models.CharField(max_length=45, verbose_name="Last name")

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Book_Rating(models.Model): #SpaT_edition
    rating_manager = models.Manager()
    user_owner = models.ForeignKey(User, related_name="rating", default=0, blank=True)
    user_rating = models.FloatField(null=0, default=0)
    common_rating = models.FloatField(null=0, default=0, blank=True)
    votes = models.IntegerField(null=0, default=0, blank=True)

    def __unicode__(self):
        return "total={0} by {1} vote(s);\ncurrent_rate={2} user: {3}".format(self.common_rating, self.votes,
                                                                              self.user_rating,
                                                                              self.user_owner.username)


class Book_Comment(models.Model):
    comments = models.Manager()
    sent_time = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, null=False)
    user = models.ForeignKey(User, related_name="comment", default=0, blank=True)

    def __unicode__(self):
        return "{0}: {1}".format(self.user.username, self.comment)


class Book(models.Model):
    books = models.Manager()
    isbn = models.CharField(max_length=13, blank=True, validators=[RegexValidator(regex="\d{13,13}",
                                                                                  message="Please just 13 digits")])
    title = models.CharField(max_length=75)
    busy = models.BooleanField(default=False)
    paperback_version_exists = models.BooleanField(default=False, verbose_name="paper version")
    description = models.TextField(max_length=255, blank=True)
    picture = ThumbnailerImageField(upload_to='book_images', blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    users = models.ManyToManyField(User, related_name="books", through=Client_Story_Record, blank=True)
    tags = models.ManyToManyField("Book_Tag", related_name="books", blank=True)
    qr_image = ThumbnailerImageField(upload_to='qr_codes', null=True, blank=True)
    book_file = models.FileField(upload_to='book_files', blank=True, null=True)
    e_version_exists = models.BooleanField(default=False, verbose_name="e version")
    book_rating = models.ManyToManyField('Book_Rating', null=None, default=None, blank=True)#SpaT_eedition
    comments = models.ManyToManyField('Book_Comment', related_name='books', default=None, blank=True) #SpaT_edition
    library = models.ForeignKey(Library, verbose_name='Library', blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def taken_about(self):
        taken = self.client_story_record_set.latest('book_taken').book_taken.date()
        now = datetime.date.today()
        return abs((taken - now).days)

    def taken_by(self):
        if self.busy:
            return self.client_story_record_set.latest('book_taken').user
        return None

    def take_by(self, client):
        self.busy = True
        new_record = Client_Story_Record.records.create(book=self, user=client)
        new_record.save()
        client.save()
        return self

    def return_by(self, client):
        self.busy = False
        record = self.client_story_record_set.latest('book_taken')
        record.book_returned = datetime.datetime.now()
        record.save()
        return self

    def common_rating(self):
        if self.book_rating.latest('id'):
            return self.book_rating.latest('id').common_rating
        return 0

    def votes_amount(self):
        if self.book_rating.latest('id'):
            return self.book_rating.latest('id').votes
        return 0





@receiver(post_save, sender=Book)
def qrcode_post_save(sender, instance, **kwargs):
        if instance.qr_image:
            return instance.qr_image
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=10,
                           border=4)
        qr.add_data(settings.DOMAIN+reverse('books:book', kwargs={'pk': instance.id}))
        qr.make(fit=True)
        image = qr.make_image()
        image_buffer = StringIO()
        image.save(image_buffer, 'PNG')
        image_buffer.seek(0)
        file_name = 'QR_%s.png' % instance.id
        file_object = File(image_buffer, file_name)
        content_file = ContentFile(file_object.read())
        instance.qr_image.save(file_name, content_file, save=True)


class Book_Tag(models.Model):
    tags = models.Manager()
    tag = models.CharField(max_length=20, unique=True, error_messages={'unique': 'Tag already exists.'})

    def __unicode__(self):
        return self.tag


def get_users_books(self):
    return self.books.filter(client_story_record__book_returned=None)

auth.models.User.add_to_class('get_users_books', get_users_books)


class Book_Request(models.Model): #SpaT_edition
    requests = models.Manager()
    user = models.ForeignKey(User, default=None, blank=True)
    users = models.ManyToManyField(User, related_name="request", default=None, blank=True)
    url = models.URLField(null='')
    title = models.CharField(max_length=30)
    vote = models.IntegerField(default=0)
    book_image_url = models.TextField(blank=True, null=True)
    book_title = models.TextField(blank=True, null=True)
    book_authors = models.TextField(blank=True, null=True)
    book_price = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return '{0} {1}'.format(self.title, self.url)


class Request_Return(models.Model):
    user_request = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    time_request = models.DateTimeField(auto_now_add=True)
    processing_time = models.DateTimeField(blank=True, null=True)



    

