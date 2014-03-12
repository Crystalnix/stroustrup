# Django settings for Books project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os.path
import warnings

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Roman', 'r.usynin@crystalnix.com'),
)

#Amazon Product Advertising API Account
AMAZON_ACCESS_KEY = "AKIAJP5RTGQPZNN5RM4Q"
AMAZON_SECRET_KEY = "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"
AMAZON_ASSOC_TAG = "520"

DOMAIN = 'stroustrup.herokuapp.com'

MANAGERS = ADMINS

BOOKS_ON_PAGE = 5
REQUEST_ON_PAGE = 3
USERS_ON_PAGE = 2
DEADLINE = 14

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 3,
    'MARGIN_PAGES_DISPLAYED': 2,
}



AUTH_USER_MODEL = 'profile.User'
AUTH_PROFILE_MODULE = 'profile.UserProfile'

THUMBNAIL_ALIASES = {
    '': {
        'avatar_size': {'size': (100, 100), 'crop': False

        },

        'avatar_profile': {'size': (36, 36), 'crop': False

         },

        'book_size': {'size': (119, 100), 'crop': False},

        'book_profile': {'size': (52, 44), 'crop': False}
}
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dbe6mv9fdteflq',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'riatxglemgeygz',
        'PASSWORD': 'etpg6fqDP6RAhuZMdmB0WCulqM',
        'HOST': 'ec2-54-197-238-239.compute-1.amazonaws.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.

        'PORT': '5432',                           # Set to empty string for default.
        'OPTIONS': {
            'autocommit': True,
        }
    }
}


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['stroustrup.herokuapp.com']

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = 'BookLibraryServer42@gmail.com'

EMAIL_HOST_PASSWORD = 'testserver42'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Omsk'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '../media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_ROOT+"/staticfiles/",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@)h98mpls4rywdtz9+8*afi30s8-d=m_ez34t*d02(^wszdvjs'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates'), )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'main.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'main.wsgi.application'


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)

INSTALLED_APPS = ('profile',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_openid_auth',
    'registration',
    'book_library',
    'profile.registration_app',

    'main',
    'pure_pagination',
    'crispy_forms',
    'south',
    'easy_thumbnails',
    'invitation',
)

warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

warnings.simplefilter('error', DeprecationWarning)

ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = [DOMAIN]

AUTHENTICATION_BACKENDS = (
            # 'django_openid_auth.auth.OpenIDBackend',
            'django.contrib.auth.backends.ModelBackend',
            'auth.GoogleBackend',
        )


OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/id'



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_FILE_PATH = 'tmp/email-messages/'

OPENID_CREATE_USERS = True

OPENID_UPDATE_DETAILS_FROM_SREG = True

LOGIN_URL = '/auth/login'

LOGIN_REDIRECT_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 2

RECAPTCHA_PRIVATE_KEY = '6LfTGuUSAAAAAB5OmCmNtYo0_CsMBozbaaoLR8Ad'

RECAPTCHA_PUBLIC_KEY = '6LfTGuUSAAAAAOpUy6YyDLTliIMo3FBAcyHGmV2K'

RECAPTCHA_USE_SSL = True

#will be implemented later

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#import dj_database_url

#DATABASES['default'] =  dj_database_url.config(default='postgres://user:pass@localhost/dbname')

try:
    from main.local_settings import *
except ImportError:
    pass