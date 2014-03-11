from django.contrib.auth.models import check_password
from openid.consumer.consumer import SUCCESS
from django.conf import settings
from django.db.models import get_model

model = settings.AUTH_USER_MODEL.split('.')
User = get_model(model[0], model[1])


class GoogleBackend:
    def authenticate(self, openid_response):
        if openid_response is None:
            return None
        if openid_response.status != SUCCESS:
            return None

        google_email = openid_response.getSigned('http://openid.net/srv/ax/1.0',  'value.email')
        google_firstname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.firstname')
        google_lastname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.lastname')
        try:
            # Make sure that the e-mail is unique.
            user = User.objects.get(email=google_email)
        except User.DoesNotExist:
            if google_email.endswith("@gmail.com"):
                if len(google_lastname) < 2:
                    username = google_email.replace("@gmail.com", "")
            else:
                username = google_firstname[0]+google_lastname
            if User.objects.filter(username=username):
                ok = False
                num = 0
                while not ok:
                    if len(username+str(num)) > 29:
                        new_username = username[:30-len(str(num)):]+str(num)
                    else:
                        new_username = username+str(num)
                    if User.objects.filter(username=new_username):
                        num += 1
                    else:
                        ok = True
                        username = new_username
            user = User.objects.create_user(username, google_email,
                                            first_name=google_firstname, last_name=google_lastname,)
            user.save()
            return user

        return user

    def get_user(self, user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class EmailAuthBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None