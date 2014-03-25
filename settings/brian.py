import os, sys, socket
from devel import *

SITE_URL = 'http://jidoor:6001'

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'trashboard',
        'USER': 'trashboard',
        'PASSWORD': 'trashboard',
        'HOST': 'IT07',
        'PORT': 1433,
        'OPTIONS': {
            'driver': 'FreeTDS',
            'host_is_server': True,
            'extra_params': 'TDS_Version=7.2;APP=Digitals',
            'unicode_results': True,
            'driver_needs_utf8': False,
        },
    }
}


INTERNAL_IPS += (('209.86.113.8'),)

INSTALLED_APPS += ('django_extensions',)


# EMAIL_HOST = '358607-exch1.protectamerica.com'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#COMPRESS_ENABLED = True
#MOCK_CREDIT=False
