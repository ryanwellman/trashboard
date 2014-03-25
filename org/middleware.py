from re import compile
from textwrap import dedent
from urllib import urlencode

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext, loader


AUTHENTICATION_MIDDLEWARE_REQUIRED = dedent(
    """\
    LoginRequiredMiddleware requires authentication middleware
    to be installed. Edit your MIDDLEWARE_CLASSES setting to insert
    'django.contrib.auth.middleware.AuthenticationMiddleware'.
    If that doesn't work, ensure your TEMPLATE_CONTEXT_PROCESSORS
    setting includes 'django.core.context_processors.auth'.
    """)

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

EXEMPT_URLS += [compile('dashboard/login/')]


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    http://djangosnippets.org/snippets/1158/

    Updates: For our purposes, any URL that does not start with dashboard/ is
    exempt from login by default.
    """

    def process_request(self, request):
        if request.META.get('HTTP_X_FORWARDED_PROTOCOL') == 'https':
            request.is_secure = lambda: True


        assert hasattr(request, 'user'), AUTHENTICATION_MIDDLEWARE_REQUIRED

        path = request.path_info.lstrip('/')
        #from pprint import pprint
        #pprint(request.__dict__)
        next = request.path_info
        if request.META['QUERY_STRING']:
            next += "?" + request.META['QUERY_STRING']
        # XXX: This is for signing, remember users don't login!
        # if not path.startswith('dashboard/'):
        #     return None

        if not request.user.is_authenticated():
            if not any(m.match(path) for m in EXEMPT_URLS):
                url = '%s?%s' % (
                    settings.LOGIN_URL,
                    urlencode({'next': next}),)
                return HttpResponseRedirect(url)


"""
Http403Middleware taken from
http://theglenbot.com/creating-a-custom-http403-exception-in-django/
"""

# Taken from https://docs.djangoproject.com/en/dev/ref/request-response/
class MultipleProxyMiddleware(object):
    FORWARDED_FOR_FIELDS = [
        'HTTP_X_REAL_IP',
        'HTTP_X_DOUBLEPROXY_IP',
        'HTTP_X_FORWARDED_FOR',
    ]

    def process_request(self, request):
        """
        Rewrites the proxy headers so that only the most
        recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                remote_addr = request.META[field].split(',')[-1]
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP'] = remote_addr
