import os, sys, socket
from devel import *

SITE_URL = 'http://cfletcher.protectamerica.com:5000'

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'HOST': 'it06\SQLEXPRESS',
        'PORT': 1433,
        'NAME': 'trashboard',
        'USER': 'trashboard',
        'PASSWORD': 'trashboard',
        'OPTIONS': {
            'driver': 'FreeTDS',
            'host_is_server': True,
            'extra_params': 'TDS_Version=8.0;APP=Intranet',
            'unicode_results': True,
            'driver_needs_utf8': False,
        },
    }
}


INTERNAL_IPS += (('209.86.112.199'),)

INSTALLED_APPS += ('django_extensions',)


# EMAIL_HOST = '358607-exch1.protectamerica.com'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#COMPRESS_ENABLED = True
