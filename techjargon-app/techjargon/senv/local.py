from techjargon.settings import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

SECRET_KEY = 'hozd=m(om6kdqgu!sq!k*=(_b2@i_&!mikksv(_21-e8o!n^(^'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'techjargon',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

AUTH_0 = {
    'CLIENT_ID': 'QADeAHqjls_NxG6lnY_MQiqJ2wErFUpx',
    'CLIENT_SECRET': '00I5NqJtwLDZBBUBXQLTYLL195BvPMDZ3uFqc6OcnunuOsyuYvI7cCQ0tORWre4a',
    'CALLBACK_URL': 'http://127.0.0.1:3000/authors/callback/'
}