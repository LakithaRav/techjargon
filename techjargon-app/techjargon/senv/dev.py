from techjargon.settings import *

DEBUG = True

ALLOWED_HOSTS = ['techjargon-dev.fidenz.info', '127.0.0.1']

SECRET_KEY = 'hozd=m(om6kdqgu!sq!k*=(_b2@i_&!mikksv(_21-e8o!n^(^'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'techjargon_dev',
        'USER': 'pgzookeeper',
        'PASSWORD': 'pgzookeeper911',
        'HOST': 'zookeeper.cilynburinur.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
    }
}

AUTH_0 = {
    'CLIENT_ID': 'QADeAHqjls_NxG6lnY_MQiqJ2wErFUpx',
    'CLIENT_SECRET': '00I5NqJtwLDZBBUBXQLTYLL195BvPMDZ3uFqc6OcnunuOsyuYvI7cCQ0tORWre4a',
    'CALLBACK_URL': 'http://techjargon-dev.fidenz.info/authors/callback/'
}