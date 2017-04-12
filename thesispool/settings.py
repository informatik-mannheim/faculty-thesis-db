import ldap
import os
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'e^#66y^5qnn))b0py#%lcpw!lvvpndbx9%7(l&fpg+17m)9pj)'

DEBUG = True

ALLOWED_HOSTS = [
    'aphrodite.informatik.hs-mannheim.de',
    'localhost',
    '127.0.0.1',
]

# Used for sending PDF files
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website.apps.WebsiteConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'thesispool.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'website/templates/website')],
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

AUTHENTICATION_BACKENDS = [
    # authenticate employees and students (frontend)
    'django_auth_ldap.backend.LDAPBackend',
    # authenticate superuser (backend)
    'django.contrib.auth.backends.ModelBackend',
]

WSGI_APPLICATION = 'thesispool.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

# LDAP-specific settings
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_START_TLS = False

# LDAP connection data
AUTH_LDAP_SERVER_URI = "ldap://ldap-master.sv.hs-mannheim.de"
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=Users,dc=informatik,dc=hs-mannheim,dc=de"
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}

LOGIN_REDIRECT_URL = '/overview/'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'de-DE'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files
STATIC_URL = '/static/'

STATICFILES_DIRs = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

from .settings_secret import *  # noqa

# For testing purposes, let faculty be a sqlite3 file to allow setup / teardown
if 'test' in sys.argv:
    DATABASES['faculty'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'students.sqlite3'),
    }
