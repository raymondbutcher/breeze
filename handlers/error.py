import traceback

import httplib
import tornado.escape
import tornado.template
import tornado.web


class ErrorHandler(tornado.web.RequestHandler):

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
        }
        if self.settings['debug']:
            if 'exc_info' in kwargs:
                context['exception'] = ''.join(traceback.format_exception(*kwargs['exc_info']))
        try:
            try:
                self.render('templates/%d.html' % status_code, **context)
            except IOError:
                self.render('templates/error.html', **context)
        except Exception:
            basic_template = tornado.template.Template(self.basic_error_template)
            self.write(basic_template.generate(**context))
