import tornado.gen
import tornado.web

from breeze.handlers import MongoRequestHandler


class AdminHandler(MongoRequestHandler):

    def get_from_key(self, key):
        if key:
            form = self.application.breeze.forms.get(key)
            if form:
                admin = self.application.breeze.admins.with_form(form)
                if admin:
                    return admin, form
            raise tornado.web.HTTPError(404, 'Admin "%s" not found.' % key)
        return None, None

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, key=None):

        admin_class, form_class = self.get_from_key(key)

        form = form_class and form_class(self)

        context = {
            'key': key,
            'current_admin': admin_class,
            'current_form': form,
            'admin_registry': self.application.breeze.admins,
            'form_registry': self.application.breeze.forms,
        }

        self.render('core/admin/admin.html', **context)

    def post(self, key):

        if not key:
            raise tornado.web.HTTPError(405, 'Form key not specified.')

        admin_class, form_class = self.get_from_key(key)

        if not form_class:
            raise tornado.web.HTTPError(404, 'Form "%s" not found.' % key)

        form = form_class(self)

        context = {
            'key': key,
            'current_admin': admin_class,
            'current_form': form,
            'admin_registry': self.application.breeze.admins,
            'form_registry': self.application.breeze.forms,
        }

        self.render('core/admin/admin.html', **context)
