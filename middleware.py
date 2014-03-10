import logging
import sys
import datetime
import uuid

from django.conf import settings

class RequestTimeLoggingMiddleware(object):
    """Middleware class logging request time to stderr.

    This class can be used to measure time of request processing
    within Django.  It can be also used to log time spent in
    middleware and in view itself, by putting middleware multiple
    times in INSTALLED_MIDDLEWARE.

    Static method `log_message' may be used independently of the
    middleware itself, outside of it, and even when middleware is not
    listed in INSTALLED_MIDDLEWARE.
    """

    @staticmethod
    def log_message(request, tag, message=''):
        """Log timing message to stderr.

        Logs message about `request' with a `tag' (a string, 10
        characters or less if possible), timing info and optional
        `message'.

        Log format is "timestamp tag uuid count path +delta message"
        - timestamp is microsecond timestamp of message
        - tag is the `tag' parameter
        - uuid is the UUID identifying request
        - count is number of logged message for this request
        - path is request.path
        - delta is timedelta between first logged message
          for this request and current message
        - message is the `message' parameter.
        """

        dt = datetime.datetime.utcnow()
        if not hasattr(request, '_logging_uuid'):
            request._logging_uuid = uuid.uuid1()
            request._logging_start_dt = dt
            request._logging_pass = 0

        request._logging_pass += 1
        print >> sys.stderr, (
            u'%s %-10s %s %2d %s +%s %s' % (
                dt.isoformat(),
                tag,
                request._logging_uuid,
                request._logging_pass,
                request.path,
                dt - request._logging_start_dt,
                message,
                )
            ).encode('utf-8')

    def process_request(self, request):
        self.log_message(request, 'request ')

    def process_response(self, request, response):
        s = getattr(response, 'status_code', 0)
        r = str(s)
        if s in (300, 301, 302, 307):
            r += ' => %s' % response.get('Location', '?')
        elif response.content:
            r += ' (%db)' % len(response.content)
        self.log_message(request, 'response', r)
        return response



from django.db import connection
from django.utils.log import getLogger

logger = getLogger(__name__)

class QueryCountDebugMiddleware(object):
    """
    This middleware will log the number of queries run
    and the total time taken for each request (with a
    status code of 200). It does not currently support
    multi-db setups.
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            total_time = 0

            for query in connection.queries:
                if getattr(settings, 'PRINT_QUERIES', False):
                    print query
                query_time = query.get('time')
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get('duration', 0) / 1000
                total_time += float(query_time)

            logger.debug('%s queries run, total %s seconds' % (len(connection.queries), total_time))
        return response