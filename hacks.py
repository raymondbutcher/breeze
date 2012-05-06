"""
Hacks for 3rd party libraries.
Not actually in-use at the moment.

"""

from functools import wraps

from tornado import httpserver
from tornado.escape import native_str, parse_qs_bytes


def http_connection_hack(original_method):
    """
    Adds blank request arguments so we can tell the difference between
    a blank value and an unsupplied value!

    """

    @wraps(original_method)
    def decorated(self, data):

        if self._request.method in ('POST', 'PUT'):
            content_type = self._request.headers.get('Content-Type', '')
            if content_type.startswith('application/x-www-form-urlencoded'):
                arguments = parse_qs_bytes(native_str(data), keep_blank_values=True)
                for name, values in arguments.iteritems():
                    has_values = bool([v for v in values if v])
                    if not has_values:
                        self._request.arguments.setdefault(name, []).extend(values)

        original_method(self, data)

    return decorated

httpserver.HTTPConnection._on_request_body = http_connection_hack(httpserver.HTTPConnection._on_request_body)


def http_request_hack(original_method):
    """
    Adds blank request arguments so we can tell the difference between
    a blank value and an unsupplied value!

    """

    @wraps(original_method)
    def decorated(self, *args, **kwargs):

        original_method(self, *args, **kwargs)

        arguments = parse_qs_bytes(self.query, keep_blank_values=True)
        for name, values in arguments.iteritems():
            self.arguments[name] = values

    return decorated

httpserver.HTTPRequest.__init__ = http_request_hack(httpserver.HTTPRequest.__init__)
