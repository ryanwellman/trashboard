# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import socket
from path import path
from datetime import timedelta
from handy.cipher import MessageCipher

import django.conf.global_settings as DEFAULT_SETTINGS


LANGUAGE_CODE = 'en-us'
USE_TZ = False
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True

INTERNAL_IPS = ('127.0.0.1',)

BASE_DIR = path(__file__).abspath().dirname().dirname()
HOSTNAME = socket.getfqdn()

MEDIA_ROOT = BASE_DIR / 'uploads'
MEDIA_URL = '/uploads/'

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = "/static/"

STATICFILES_DIRS = (
    BASE_DIR / 'assets',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hdi%asicub%e1z$=9h&g&m8$m$n2+bwo*_gne2zqbt5-+u+!##'

MIDDLEWARE_CLASSES = (
    'middleware.RequestTimeLoggingMiddleware',
    'middleware.QueryCountDebugMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dynamicresponse.middleware.api.APIMiddleware',
    'dynamicresponse.middleware.dynamicformat.DynamicFormatMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    BASE_DIR / 'templates',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',
    'compressor',
    'raven.contrib.django.raven_compat',

    'org',
    'inventory',
    'agreement',
    'handy',
    'regional',
)

# This is tacked onto the end of COMPRESS_ROOT (which defaults to STATIC_ROOT)
COMPRESS_OUTPUT_DIR = '_cache'

if HOSTNAME == 'secure.protectamerica.com':
    LESSC_BIN = ";lasdkfasd;lk"
else:
    LESSC_BIN = "lessc"

COMPRESS_PRECOMPILERS = (
    ('text/less', '{0} {{infile}} {{outfile}}'.format(LESSC_BIN)),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]


TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(process)d '
                       '%(thread)d %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

CREDIT_BUREAUS = 'equifax,transUnion'
STOP_RUNNING_AT_BEACON = 625
CREDIT_REUSABLE_SPAN = timedelta(days=30)
CREDIT_APPROVED_BEACON = 600

SOCIAL_CIPHER = MessageCipher(private_file='/devd/trashboard/social_cipher_test.private', public_file='/devd/trashboard/social_cipher_test.public')

