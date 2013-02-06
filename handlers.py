import asyncmongo
import httplib
import tornado.escape
import tornado.template
import tornado.web
import traceback

from tornado.options import options


class AuthMixin(object):

    def clear_auth_cookies(self):
        """Clear all auth cookies, logging the user out."""
        self.clear_cookie('auth')
        self.clear_cookie('auth_staff')
        self.clear_cookie('auth_superuser')

    def get_current_user(self):
        """
        Return the user's email address if they are logged in.
        This is not returning an actual user object because that
        needs to be done asynchronously.
        """
        return self.get_secure_cookie('auth')

    def set_auth_cookies(self, user):
        """Set all necessary auth cookies for the given user."""

        self.set_secure_cookie('auth', user['email'])

        if user.get('staff'):
            self.set_secure_cookie('auth_staff', '1')
        else:
            self.clear_cookie('auth_staff')

        if user.get('superuser'):
            self.set_secure_cookie('auth_superuser', '1')
        else:
            self.clear_cookie('auth_superuser')


class ErrorMixin(object):

    basic_error_template = tornado.escape.squeeze('''
    <html>
        <head>
            <title>{{ code }}: {{ message }}</title>
        </head>
        <body>
            <h1>
                {{ code }}: {{ message }}
            </h1>
            {% if exception %}
            <pre>{% raw exception %}</pre>
            {% end %}
        </body>
    </html>
    ''').strip()

    def write_error(self, status_code, **kwargs):
        context = {
            'code': status_code,
            'message': httplib.responses[status_code],
            'exception': '',
        }
        if 'exc_info' in kwargs:
            context['error_object'] = kwargs['exc_info'][1]
            if self.settings['debug']:
                context['exception'] = ''.join(traceback.format_exception(*kwargs['exc_info']))
        try:
            try:
                self.render('breeze/errors/%d.html' % status_code, **context)
            except IOError:
                self.render('breeze/errors/error.html', **context)
        except Exception:
            basic_template = tornado.template.Template(self.basic_error_template)
            self.write(basic_template.generate(**context))


class MongoMixin(object):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(
                pool_id='breeze',
                host=options.mongo_host,
                port=options.mongo_port,
                maxcached=10,
                maxconnections=50,
                dbname=options.mongo_dbname,
                dbuser=options.mongo_dbuser,
                dbpass=options.mongo_dbpass,
            )
        return self._db

    @staticmethod
    def get_mongo_result(gen_result, allow_none=False):
        args, kwargs = gen_result
        error = kwargs.get('error')
        if error:
            raise tornado.web.HTTPError(500, unicode(error))
        result = args[0]
        if not result:
            if allow_none:
                return None
            raise tornado.web.HTTPError(404, 'Object not found')
        return result


class RequestHandler(ErrorMixin, AuthMixin, tornado.web.RequestHandler):
    pass


class MongoRequestHandler(MongoMixin, RequestHandler):
    pass
