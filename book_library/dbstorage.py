from django.core.files.storage import Storage
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.exceptions import ObjectDoesNotExist
from main.models import FileStorage
import StringIO
import urlparse
from django.core.files import File
import mimetypes


class DatabaseStoragePostgres(Storage):

    def __init__(self):
        self.base_url = settings.DB_FILES_URL

    def _open(self, name, mode='rb'):

        assert mode == 'rb', "You've tried to open binary file without specifying binary mode! You specified: %s" % mode
        try:
            media_file = FileStorage.objects.get(file_name=name)
        except ObjectDoesNotExist:
            return None
        inMemFile = StringIO.StringIO(media_file.blob)
        inMemFile.name = name
        inMemFile.mode = mode
        retFile = File(inMemFile)
        return retFile

    def exists(self, name):
        blob = FileStorage.objects.filter(file_name=name)
        return blob

    def _save(self, name, content):
        name = name.replace('\\', '/')
        binary = content.read()
        size = content.size
        blob_exist = self.exists(name)

        if blob_exist:
            blob_exist.update(blob=binary, size=size)
        else:
            FileStorage.objects.create(file_name=name, blob=binary, size=size)
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
    image_file = storage.open(filename, 'rb')
    if image_file is None:
        raise Http404
    else:
        file_content = image_file.read()
    if request.META.get('HTTP_IF_MODIFIED_SINCE') is not None:
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(filename)
    content_type = content_type or 'application/octet-stream'
    response = HttpResponse(file_content, content_type=content_type)
    response['Content-Disposition'] = 'inline; filename=%s' % filename
    return response