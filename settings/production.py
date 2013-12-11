from common import *

ADMINS = (
    ('Developers', 'development@protectamerica.com'),
)

EMAIL_HOST = '358607-exch1.protectamerica.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SERVER_EMAIL = "root@dashboard.protectamerica.com"

RAVEN_CONFIG = {
    'dsn': 'http://89ca842f479b4c438c68ce1343cfe0a1:772d82ff114a413f9b1209956268153f@panic.protectamerica.com/4',
}

LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['sentry'],
}

LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'raven.contrib.django.handlers.SentryHandler',
}

LOGGING['loggers']['raven'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

LOGGING['loggers']['sentry.errors'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}
