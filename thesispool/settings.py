import ldap
from django_auth_ldap.config import *
import os
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = [
    'aphrodite.informatik.hs-mannheim.de',
    'thesis.informatik.hs-mannheim.de',
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
    'approvals.apps.ApprovalsConfig'
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

AUTH_USER_MODEL = 'website.User'

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

# allow self signed certs
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

# LDAP-specific settings
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_START_TLS = True


AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=informatik,dc=hs-mannheim,dc=de",
                                    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
                                    )
AUTH_LDAP_GROUP_TYPE = PosixGroupType()


# LDAP connection data
AUTH_LDAP_SERVER_URI = "ldap://ldap-master.sv.hs-mannheim.de"
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=Users,dc=informatik,dc=hs-mannheim,dc=de"
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName",
                           "last_name": "sn",
                           "initials": "initials"}


AUTH_LDAP_PROF_DN = "cn=profI,ou=groups,dc=informatik,dc=hs-mannheim,dc=de"

# map group permissions
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_prof": AUTH_LDAP_PROF_DN,
    "is_staff": "cn=staff,ou=groups,dc=informatik,dc=hs-mannheim,dc=de",
    "is_secretary": "cn=sekretariat,ou=groups,dc=informatik,dc=hs-mannheim,dc=de",
    "is_excom": "cn=excom,ou=groups,dc=informatik,dc=hs-mannheim,dc=de",
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True

# Simple group restrictions
#AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
AUTH_LDAP_DENY_GROUP = "cn=students,ou=groups,dc=informatik,dc=hs-mannheim,dc=de"


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
