from django.core.files.storage import Storage
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.exceptions import ObjectDoesNotExist
from main.models import FileStorage
import StringIO
import urlparse
from django.core.files import File
import mimetypes
import os


class DatabaseStoragePostgres(Storage):

    def __init__(self):
        self.base_url = settings.DB_FILES_URL

    def _open(self, name, mode='rb'):
        assert mode == 'rb', "You've tried to open binary file without specifying binary mode! You specified: %s" % mode
        try:
            media_file = FileStorage.objects.get(file_name=name)
        except ObjectDoesNotExist:
            return None
        content_type = media_file.content_type
        inMemFile = StringIO.StringIO(media_file.blob)
        inMemFile.name = name
        inMemFile.mode = mode
        retFile = File(inMemFile)
        retFile.content_type = content_type
        return retFile

    def exists(self, name):
        return FileStorage.objects.filter(file_name=name).exists()

    def _save(self, name, content):
        name = name.replace('\\', '/')
        content_type, encoding = mimetypes.guess_type(name)
        content_type = content_type or 'application/octet-stream'
        binary = content.read()
        size = content.size
        count = 0
        head, tail = os.path.splitext(name)
        while self.exists(name):
            count += 1
            name = '%s_%d%s' % (head, count, tail)
        FileStorage.objects.create(file_name=name, blob=binary, content_type=content_type, size=size)
        return name

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')

    def get_available_name(self, name):
        return name

    def delete(self, name):
        FileStorage.objects.filter(file_name=name).delete()


def file_view(request, filename):
    storage = DatabaseStoragePostgres()
    file_object = storage.open(filename, 'rb')
    if file_object is None:
        raise Http404
    else:
        file_content = file_object.read()
    response = HttpResponse(file_content, content_type=file_object.content_type)
    response['Content-Disposition'] = 'inline; filename=%s' % filename
    return response