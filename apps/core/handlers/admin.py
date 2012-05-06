import tornado.gen
import tornado.web

from breeze.handlers import MongoRequestHandler


class AdminHandler(MongoRequestHandler):

    def initialize(self, require_authentication=True):
        if require_authentication:
            self.handle_method = self.handle_request_authenticated
        else:
            self.handle_method = self.handle_request

    @tornado.web.asynchronous
    @tornado.gen.engine
    def handle_request(self, key, require_form=False):

        if key:
            form_class = self.application.breeze.forms.get(key)
            if form_class:

                # Create the form instance, passing in this handler so it can
                # access request data and the mongo database etc.
                current_form = yield tornado.gen.Task(form_class, self)

                # Call the form itself, performing an action if requested.
                yield tornado.gen.Task(current_form)

                # An action is able to finish a request, by rendering a page or
                # redirecting to another page. If that happened, then there
                # is no need to continue running the rest of this method.
                if self._finished:
                    return

            else:
                raise tornado.web.HTTPError(404, 'Form "%s" not found.' % key)
        elif require_form:
            raise tornado.web.HTTPError(405, 'Form key not specified.')
        else:
            current_form = None

        # Find which admin has this form.
        if current_form:
            current_admin = self.application.breeze.admins.with_form(current_form)
        else:
            current_admin = None

        # And now render the admin/form.
        context = {
            'key': key,
            'current_admin': current_admin,
            'current_form': current_form,
            'admin_registry': self.application.breeze.admins,
            'form_registry': self.application.breeze.forms,
        }
        self.render('core/admin/admin.html', **context)

    handle_request_authenticated = tornado.web.authenticated(handle_request)

    def get(self, key=None):
        self.handle_method(key)

    def post(self, key):
        self.handle_method(key, require_form=True)
