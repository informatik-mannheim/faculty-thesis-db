import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '!1aq=)8i5b4!gzl7r8hgl51%1r7^t01mow)#l_p=941$idkpmq'

DATABASES = {
    'faculty': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'thesisuser',
        'PASSWORD': 'YShy9MuftKYnctTs',
        'HOST': 'intern.informatik.hs-mannheim.de',
        'NAME': 'sl',
    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

DEBUG = True
AUTH_LDAP_START_TLS = False
