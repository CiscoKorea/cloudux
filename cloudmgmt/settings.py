"""
Django settings for cisco02 project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
#import ldap
#from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&cwvz^e28!%nv4lnqlew8-)ckv4e!)$nz%so1q3-=9=f90@rz&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ux',
    'cloudmgmt',
    'djcelery',
    'kombu.transport.django'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloudmgmt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloudmgmt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

import ConfigParser
import os
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'connection.cfg'))
hostname = config.get('mysql', "hostname")
dbname = config.get('mysql', "dbname")
username = config.get('mysql', "username")
password = config.get('mysql', "password")
port = config.get('mysql', "port")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': dbname,
        'USER': username,
        'PASSWORD': password,
        'HOST': hostname,
        'PORT': port,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ko-KR'

LANGUAGES = [
    ('ko', _('Korean')),
    ('en', _('English')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/resources/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
     # ('resources', os.path.join(BASE_DIR, 'resources'),),
)

# #### Celery CONFIGURATION
## Broker settings.
BROKER_URL = 'django://'

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = "sqlite:///mydatabase.db"


CELERY_ANNOTATIONS = {'cloudmgmt.tasks.add': {'rate_limit': '10/s'}}
from datetime import timedelta

t1 = 20
t2 = 10

CELERYBEAT_SCHEDULE = {
    'update-all': {
        'task': 'cloudmgmt.tasks.update_all',
        'schedule': timedelta(minutes=5),  # minutes=10
        'args': ()
    },
    'update-hosts': {
        'task': 'cloudmgmt.tasks.update_hosts',
        'schedule': timedelta(minutes=10),
        'args': ()
    },
    'update-vms': {
        'task': 'cloudmgmt.tasks.update_vms',
        'schedule': timedelta(minutes=15),
        'args': ()
    },
}
# #### END Celery CONFIGURATION



LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

LOGOUT_REDIRECT_URL = '/'
LOGOUT_URL = '/logout'



AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://ldap.example.local"

AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=development,dc=example,dc=local",
#    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=development,dc=example,dc=local",
#     ldap.SCOPE_SUBTREE, "(objectClass=partone)"
# )
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
